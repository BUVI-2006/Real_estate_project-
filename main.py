import uvicorn 
from fastapi import FastAPI
import json 
from Model import model
import numpy as np 
import pickle 


app=FastAPI()

file=open('properties.json','r')
properties=json.load(file)
file.close()


listing=open('city_listing_count.json','r')
city_listing_count=json.load(listing)

with open("max_log_size_sqm.pkl","rb") as f2:
          max_log_size_sqm=pickle.load(f2)

with open("velocity_model.pkl","rb") as velocity:
       velocity_model=pickle.load(velocity)

with open("liquidity_model.pkl","rb") as liquidity:
       liquidity_mode1=pickle.load(liquidity)

with open("ranking_model.pkl","rb") as ranking:
       ranking_model=pickle.load(ranking)








# exposing the existing top 10 states (as data is unavailable )

@app.get('/')
def index():
    return {'API':"Accessing the real estate ranking system",
            "/properties/top10":"  JSON of top 10 estates",
             "/properties/all":"JSON of all the estates (1 lakh rows currently)",
             "/predict":"JSON of tree model predictions"}






@app.get("/properties/top10")
def get_top():
    
    return properties[:10]

@app.get("/properties/all")
def others():
    return properties


@app.post('/predict')
def predict(data:model):
      data=data.model_dump()
      property_id=data["property_id"]
      city=data["city"]
      commercial_type=data["commercial_type"]   
      size_sqm=data["size_sqm"]
      annual_rent=data["annual_rent"]
      occupancy_status=data["occupancy_status"]
      lease_term_years=data["lease_term_years"]

     
      occupancy_status=(1 if occupancy_status=='vacant' else 0)  

      com_arr=['office', 'retail_shop', 'showroom', 'warehouse']

      com_map = {value: idx for idx, value in enumerate(com_arr)}
      
      

      com_encoded=com_map.get(commercial_type,-1)

      

      rent_sqm=annual_rent/size_sqm
      lease_term_short=1 if lease_term_years<2 else 0
      log_size_sqm=np.log(size_sqm)

      global_median= np.median(list(city_median_map.values()))
      global_count = np.median(list(city_count_map.values()))


      city_median=city_median_map.get(city,global_median)
      city_count=city_count_map.get(city,global_count)

      mispricing_score = abs(rent_sqm - city_median) / city_median

    
      

     

      velocity_score=velocity_model.predict([[rent_sqm, log_size_sqm, city_median, city_count, lease_term_short]])[0]
      liquidity_score=liquidity_mode1.predict([[rent_sqm, log_size_sqm, lease_term_short, city_count]])[0]
      ranking_score=ranking_model.predict([[log_size_sqm, lease_term_short, city_count, city_median, com_encoded]])[0]

      return {
          "velocity_score":float(velocity_score),
          "liquidity_score":float(liquidity_score),
          "ranking_score":float(ranking_score)
      }




if __name__=="__main__":
    uvicorn.run(app,host="127.0.0.1",port=8000,reload=True)