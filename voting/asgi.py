import os
from django.core.asgi import get_asgi_application
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from django.urls import re_path
from starlette.middleware.wsgi import WSGIMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eBallot.settings')

# Initialize FastAPI app
fastapi_app = FastAPI()

# CORS configuration
fastapi_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# FastAPI routes
@fastapi_app.get("/get-countries/")
async def get_countries():
    import requests
    response = requests.get("https://restcountries.com/v3.1/all")
    if response.status_code == 200:
        countries = response.json()
        results = [{"country": country.get('name', {}).get('common', '')} for country in countries if 'name' in country]
        return {"countries": results}
    return {"error": "Failed to fetch country data"}

@fastapi_app.get("/get-regions/")
async def get_regions(country: str):
    import requests
    response = requests.get("https://restcountries.com/v3.1/all")
    if response.status_code == 200:
        countries = response.json()
        for country_data in countries:
            if country.lower() == country_data.get('name', {}).get('common', '').lower():
                region = country_data.get('region', 'Unknown Region')
                return {"regions": [region]}
        return {"regions": []}
    return {"error": "Failed to fetch region data"}

# Create Django ASGI app
django_app = get_asgi_application()

# Mount FastAPI under /api and keep Django running
from starlette.routing import Mount
from starlette.applications import Starlette

application = Starlette(routes=[
    Mount("/api", app=fastapi_app),
    Mount("/", app=WSGIMiddleware(django_app)),  # Django is still the main app
])
