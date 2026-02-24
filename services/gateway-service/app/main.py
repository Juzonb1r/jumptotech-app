from fastapi import FastAPI
from fastapi.responses import JSONResponse
import httpx
import os

app = FastAPI(title="gateway-service")

SERVICES = {
    "auth": "http://auth-service:8000",
    "courses": "http://courses-service:8000",
    "enrollment": "http://enrollment-service:8000",
    "content": "http://content-service:8000",
    "news": "http://news-service:8000",
}

@app.get("/health")
def health():
    return {"status": "ok", "service": "gateway-service"}

@app.get("/{service}/health")
async def proxy_health(service: str):
    if service not in SERVICES:
        return JSONResponse(status_code=404, content={"error": "service not found"})

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVICES[service]}/health")
        return response.json()