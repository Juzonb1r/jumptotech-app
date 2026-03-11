from fastapi import FastAPI
from fastapi.responses import JSONResponse, PlainTextResponse, Response
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import httpx

app = FastAPI(title="gateway-service")

REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["service", "path", "method"]
)

SERVICES = {
    "auth": "http://auth-service:8000",
    "courses": "http://courses-service:8000",
    "enrollment": "http://enrollment-service:8000",
    "content": "http://content-service:8000",
    "news": "http://news-service:8000",
}


@app.middleware("http")
async def metrics_middleware(request, call_next):
    response = await call_next(request)
    REQUESTS.labels(service="gateway-service", path=request.url.path, method=request.method).inc()
    return response


@app.get("/health")
def health():
    return {"status": "ok", "service": "gateway-service"}


@app.get("/metrics")
def metrics():
    data = generate_latest()
    return PlainTextResponse(content=data.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)


@app.get("/api/courses")
async def proxy_courses():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVICES['courses']}/courses")
        return Response(
            content=response.content,
            status_code=response.status_code,
            media_type=response.headers.get("content-type", "application/json")
        )


@app.get("/{service}/health")
async def proxy_health(service: str):
    if service not in SERVICES:
        return JSONResponse(status_code=404, content={"error": "service not found"})

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SERVICES[service]}/health")
        return response.json()