import uvicorn 
from fastapi import FastAPI
import json 
from Model import model
import numpy as np 
import pickle 
from groq import Groq 
import os 
from dotenv import load_dotenv



app=FastAPI()

file=open('properties.json','r')
properties=json.load(file)
file.close()


listing=open('city_listing_count.json','r')
city_count_map=json.load(listing)
listing.close()





city_median=open('city_median_map.json','r')
city_median_map=json.load(city_median)

with open("velocity_model.pkl","rb") as velocity:
       velocity_model=pickle.load(velocity)

with open("liquidity_model.pkl","rb") as liquidity:
       liquidity_mode1=pickle.load(liquidity)

with open("ranking_model.pkl","rb") as ranking:
       ranking_model=pickle.load(ranking)





client=Groq(api_key=os.getenv("API_KEY"))




# exposing the existing top 10 states (as data is unavailable )

@app.get('/')
def index():
    return {'API':"Accessing the real estate ranking system",
            "/properties/top10":"  JSON of top 10 estates",
             "/properties/all":"JSON of all the estates (1 lakh rows currently)",
             "/recommend":"Provides a recommendation based on the calculated scores "}






@app.get("/properties/top10")
def get_top():
    
    return properties[:10]

@app.get("/properties/all")
def others():
    return properties


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

      global_median= np.median(list(city_median_map.values()))
      global_count = np.median(list(city_count_map.values()))


      city_median=city_median_map.get(city,global_median)
      city_count=city_count_map.get(city,global_count)

      
    
      

     

      velocity_score=velocity_model.predict([[rent_sqm, log_size_sqm, city_median, city_count, lease_term_short]])[0]
      liquidity_score=liquidity_mode1.predict([[rent_sqm, log_size_sqm, lease_term_short, city_count]])[0]
      ranking_score=ranking_model.predict([[log_size_sqm, lease_term_short, city_count, city_median, com_encoded]])[0]


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
    uvicorn.run(app,host="127.0.0.1",port=8000,reload=True)
