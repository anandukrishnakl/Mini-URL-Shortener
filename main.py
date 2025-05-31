from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
import string, random

app = FastAPI()

# Temporary in-memory database
url_db = {}

class URLRequest(BaseModel):
    url: HttpUrl

class URLResponse(BaseModel):
    short_url: str

def generate_short_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

@app.post("/shorten", response_model=URLResponse)
def shorten_url(request: URLRequest):
    short_code = generate_short_code()
    url_db[short_code] = request.url
    return {"short_url": f"http://localhost:8000/r/{short_code}"}

@app.get("/r/{short_code}")
def redirect_url(short_code: str):
    original_url = url_db.get(short_code)
    if original_url:
        return RedirectResponse(url=original_url)
    raise HTTPException(status_code=404, detail="Short URL not found")
