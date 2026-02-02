import uvicorn 
from fastapi import FastAPI
import json 
from Model import model
import numpy as np 


app=FastAPI()

file=open('properties.json','r')
properties=json.load(file)






# exposing the existing top 10 states (as data is unavailable )

@app.get('/')
def index():
    return {'API':"Accessing the real estate ranking system",
            "/properties/top10":"  JSON of top 10 estates",
             "/properties/all":"JSON of all the estates (1 lakh rows currently)"}






@app.get("/properties/top10")
def get_top():
    
    return properties[:10]

@app.get("/properties/all")
def others():
    return properties


@app.post('/predict')
def predict(data:model):
      data=data.model_dump()
      property_id=data.property_id
      city=data.city
      commercial_type=data.commercial_type
      size_sqm=data.size_sqm
      annual_rent=data.annual_rent
      occupancy_status=data.occupancy_status
      lease_term_years=data.lease_term_years

      occupancy_status=(1 if occupancy_status=='vacant' else 0)  # array(['office', 'retail_shop', 'showroom', 'warehouse'], dtype=object)
      com_arr=['office', 'retail_shop', 'showroom', 'warehouse']
      
      com_map = {value: idx for idx, value in enumerate(com_arr)}

      rent_sqm=annual_rent/size_sqm
      lease_term_short=np.where 



       
      

            
          
    




if __name__=="__main__":
    uvicorn.run(app,host="127.0.0.1",port=8000,reload=True)