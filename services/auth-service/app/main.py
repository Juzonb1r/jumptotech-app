from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import os

SERVICE = os.getenv("SERVICE_NAME", "auth-service")

app = FastAPI(title=SERVICE)

REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["service", "path", "method"]
)

@app.middleware("http")
async def metrics_middleware(request, call_next):
    response = await call_next(request)
    REQUESTS.labels(
        service=SERVICE,
        path=request.url.path,
        method=request.method
    ).inc()
    return response

@app.get("/health")
def health():
    return {"status": "ok", "service": SERVICE}

@app.get("/metrics")
def metrics():
    data = generate_latest()
    return PlainTextResponse(
        content=data.decode("utf-8"),
        media_type=CONTENT_TYPE_LATEST
    )