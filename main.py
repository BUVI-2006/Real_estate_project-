import uvicorn 
from fastapi import FastAPI
import json 
from Model import model
import numpy as np 
import pickle 
from groq import Groq 
import os 
from dotenv import load_dotenv 
from supabase import create_client 


load_dotenv()

app=FastAPI()





with open("velocity_model.pkl","rb") as velocity:
       velocity_model=pickle.load(velocity)

with open("liquidity_model.pkl","rb") as liquidity:
       liquidity_mode1=pickle.load(liquidity)

with open("ranking_model.pkl","rb") as ranking:
       ranking_model=pickle.load(ranking)

with open("priority_model.pkl","rb") as priority:
     priority_model=pickle.load(priority)


SUPABASE_URL="https://vgvhzoccmvvasdruciks.supabase.co"
SUPABASE_KEY=os.getenv("db_key")

# Transferring the entire data to supabase.
client=Groq(api_key=os.getenv("API_KEY"))

supabase=create_client(SUPABASE_URL,SUPABASE_KEY)


@app.get('/')
def index():
    return {'API':"Accessing the real estate ranking system",
            "/recommend":"Get all the user details and predict the asset status"}



@app.get("/health")
def get_top():
    
    return {"status":"good"}



@app.post('/recommend')
def predict(data:model):
      data=data.model_dump()
      property_id=data["property_id"]
      city=data["city"]
      commercial_type=data["commercial_type"]   
      size_sqm=data["size_sqm"]
      annual_rent=data["annual_rent"]
      occupancy_status=data["occupancy_status"]
      lease_term_years=data["lease_term_years"]
      listing_date=data["listing_date"]

     
      occupancy_status=(1 if occupancy_status.lower()=='vacant' else 0)  

      com_arr=['office', 'retail_shop', 'showroom', 'warehouse']

      com_map = {value: idx for idx, value in enumerate(com_arr)}

      com_encoded=com_map.get(commercial_type,-1)

      
      if size_sqm>0:
        rent_sqm=annual_rent/size_sqm
      else :
        return {"error":"size_sqm is zero"}
      
      lease_term_short=1 if lease_term_years<2 else 0
      log_size_sqm=np.log(size_sqm)

      try:
        response=supabase.table("metrics").select("city_median_rent","city_count").eq("city",city).single().execute()
     
        if response.data:
            median=response.data["city_median_rent"]
            count=response.data["city_count"]

        else :
            median=rent_sqm
            count=1

      except Exception:    # in rare cases 
          median,count=0,0



      cols = [
    "liquidity_score",
    "velocity_score",
    "rent_sqm",
    "city_median_rent_sqm",
    "city_listing_count",
    "log_size_sqm",
    "lease_term_years",
    "occupancy_status",
    "commercial_type"
     ]

      velocity_score=velocity_model.predict([[rent_sqm, log_size_sqm, median, count, lease_term_short]])[0]
      liquidity_score=liquidity_mode1.predict([[rent_sqm, log_size_sqm, lease_term_short,count]])[0]
      ranking_score=ranking_model.predict([[log_size_sqm, lease_term_short,count, median, com_encoded]])[0]
      priority_rank=priority_model.predict([[liquidity_score,velocity_score,rent_sqm,median,count,log_size_sqm,lease_term_years,occupancy_status,com_encoded]])

      if priority_rank==0:
       priority="Low Priority"

      elif priority_rank==1:
       priority="Watchlist"
      
      elif priority_rank==2:
       priority="High Priority"
      
      else :
       priority="Immediate Action"

      #Storing in Supabase 
      user_data={
          "property_id":property_id,
          "listing_date":listing_date,
          "city":city,
          "commercial_type":commercial_type,
          "size_sqm":size_sqm,
          "annual_rent":annual_rent,
          "occupancy_status":occupancy_status,
          "lease_term_years":lease_term_years,
          "rent_sqm":rent_sqm,
          "priority":priority,  
      }

      try:
       supabase.table('properties').insert(user_data).execute()
       print(f"data entered")
      except Exception as e:
    # This will print the exact reason (e.g., "duplicate key value" or "permission denied")
         print(f"Supabase Error: {e}")
       

      prompt = f"""
  You are a market recommendation engine for commercial land assets.

Audience:
Non-technical buyers and sellers.

Context:
The following scores are produced by predictive models trained on historical transaction data.
They indicate relative performance, not exact probabilities.

Rules:
- Use simple, market-facing language.
- Use numbers only where they add clarity.
- Do NOT explain model mechanics.
- Do NOT convert scores directly into percentages.
- Avoid technical terms like “distribution”, “quartile”, “median”.
- Speak in terms of speed, demand, and positioning.

Objective:
Provide a clear, neutral recommendation that helps both buyers and sellers
understand how this asset is likely to perform in the market.

Inputs:
- Velocity Score: {velocity_score}
- Liquidity Score: {liquidity_score}
- Ranking Score: {ranking_score}
- Priority Label:{priority}

Output style:
- 2 to 3 short paragraphs
- Plain English
- Calm, factual, confidence-building
- No hype, no fear, no emotions


     """



      completion=client.chat.completions.create(
           model="openai/gpt-oss-120b",
           messages=[
                {"role":"user","content":prompt}
           ],
           temperature=0,
           top_p=1,
           max_completion_tokens=500
      )

      return {
           "recommendation":completion.choices[0].message.content           
      }



if __name__=="__main__":
    uvicorn.run(app,host="0.0.0.0",port=10000,reload=True)
