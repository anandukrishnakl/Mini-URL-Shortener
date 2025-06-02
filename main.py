from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
from azure.cosmos import CosmosClient, PartitionKey, exceptions
import os, string, random
from datetime import datetime, timedelta
import sys

app = FastAPI()

# Configuration loader (same as setup_db.py)
def load_config():
    # 1. Try manual read first
    try:
        with open('.env', 'rb') as f:
            config = {
                line.decode('utf-8').strip().split('=', 1)[0]:
                line.decode('utf-8').strip().split('=', 1)[1]
                for line in f
                if b'=' in line
            }
        if all(k in config for k in ['COSMOS_ENDPOINT', 'COSMOS_KEY']):
            return config
    except:
        pass
    
    # 2. Fallback to os.environ
    import os
    config = {
        'COSMOS_ENDPOINT': os.getenv('COSMOS_ENDPOINT'),
        'COSMOS_KEY': os.getenv('COSMOS_KEY')
    }
    if all(config.values()):
        return config
    
    # 3. Final fallback to dotenv
    try:
        from dotenv import dotenv_values
        config = dotenv_values('.env')
        if all(k in config for k in ['COSMOS_ENDPOINT', 'COSMOS_KEY']):
            return config
    except:
        pass
    
    raise ValueError("Could not load configuration")

# Load configuration
try:
    config = load_config()
    client = CosmosClient(config['COSMOS_ENDPOINT'], config['COSMOS_KEY'])
    database = client.get_database_client('urlshortenerdb')
    container = database.get_container_client('urls')
except Exception as e:
    print(f"Failed to initialize Cosmos DB: {str(e)}")
    sys.exit(1)

class URLRequest(BaseModel):
    url: HttpUrl
    expiration_days: int = 30

@app.post("/shorten")
async def shorten_url(request: URLRequest):
    short_code = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    expiration = datetime.utcnow() + timedelta(days=request.expiration_days)
    
    try:
        container.upsert_item({
            'id': short_code,
            'original_url': str(request.url),
            'created_at': datetime.utcnow().isoformat(),
            'expires_at': expiration.isoformat(),
            'clicks': 0
        })
        return {
            "short_url": f"/r/{short_code}",
            "expiration": expiration.isoformat()
        }
    except exceptions.CosmosHttpResponseError as e:
        raise HTTPException(status_code=500, detail="Database error")

@app.get("/r/{short_code}")
async def redirect_url(short_code: str):
    try:
        item = container.read_item(short_code, partition_key=short_code)
        item['clicks'] += 1
        container.upsert_item(item)
        return RedirectResponse(url=item['original_url'])
    except exceptions.CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail="Short URL not found")
    except exceptions.CosmosHttpResponseError:
        raise HTTPException(status_code=500, detail="Database error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
