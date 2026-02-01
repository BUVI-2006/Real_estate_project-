import uvicorn 
from fastapi import FastAPI
import json 


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


if __name__=="__main__":
    uvicorn.run(app,host="127.0.0.1",port=8000,reload=True)