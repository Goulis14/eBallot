from fastapi import FastAPI
import requests
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Restcountries API URL
COUNTRIES_API_URL = "https://restcountries.com/v3.1/all"

@app.get("/get-countries/")
def get_countries():
    response = requests.get(COUNTRIES_API_URL)
    if response.status_code == 200:
        countries = response.json()
        results = [{"country": country.get('name', {}).get('common', '')} for country in countries if 'name' in country]
        return {"countries": results}
    return {"error": "Failed to fetch country data"}

@app.get("/get-regions/")
def get_regions(country: str):
    response = requests.get(COUNTRIES_API_URL)
    if response.status_code == 200:
        countries = response.json()
        for country_data in countries:
            if country.lower() == country_data.get('name', {}).get('common', '').lower():
                region = country_data.get('region', 'Unknown Region')
                return {"regions": [region]}  # Return list with one region for consistency
        return {"regions": []}  # Return empty list instead of an error
    return {"error": "Failed to fetch region data"}
