from pydantic import BaseModel



class model(BaseModel):

    

    property_id:str
    city:str
    commercial_type:str
    size_sqm:int
    annual_rent:int
    occupancy_status:str
    lease_term_years:int


