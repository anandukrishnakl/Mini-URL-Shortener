from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from azure.cosmos import CosmosClient, exceptions
import os, string, random
from datetime import datetime, timedelta

app = FastAPI()

# Cosmos DB Configuration
COSMOS_ENDPOINT = os.getenv("COSMOS_ENDPOINT")
COSMOS_KEY = os.getenv("COSMOS_KEY")
DATABASE_NAME = "urlshortenerdb"
CONTAINER_NAME = "urls"

client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
database = client.get_database_client(DATABASE_NAME)
container = database.get_container_client(CONTAINER_NAME)

class URLRequest(BaseModel):
    url: HttpUrl
    expiration_days: int = 30  # Default expiration

class URLResponse(BaseModel):
    short_url: str
    expiration: str

def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

@app.post("/shorten", response_model=URLResponse)
async def shorten_url(request: URLRequest):
    short_code = generate_short_code()
    expiration = datetime.utcnow() + timedelta(days=request.expiration_days)
    
    try:
        container.upsert_item({
            'id': short_code,
            'original_url': str(request.url),
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': expiration.isoformat(),
            'clicks': 0
        })
    except exceptions.CosmosHttpResponseError as e:
        raise HTTPException(status_code=500, detail="Database error")

    return {
        "short_url": f"https://webapp-urlshortener.azurewebsites.net/r/{short_code}",
        "expiration": expiration.isoformat()
    }

@app.get("/r/{short_code}")
async def redirect_url(short_code: str):
    try:
        item = container.read_item(short_code, partition_key=short_code)
        
        # Update click count
        item['clicks'] += 1
        container.upsert_item(item)
        
        return RedirectResponse(url=item['original_url'])
        
    except exceptions.CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail="Short URL not found")
    except exceptions.CosmosHttpResponseError:
        raise HTTPException(status_code=500, detail="Database error")

@app.get("/stats/{short_code}")
async def get_stats(short_code: str):
    try:
        item = container.read_item(short_code, partition_key=short_code)
        return {
            "clicks": item['clicks'],
            "created_at": item['created_at'],
            "expires_at": item['expires_at']
        }
    except exceptions.CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail="Short URL not found")