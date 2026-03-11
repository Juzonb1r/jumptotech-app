from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import os
import psycopg2
from psycopg2.extras import RealDictCursor

SERVICE = os.getenv("SERVICE_NAME", "courses-service")
DB_HOST = os.getenv("DB_HOST", "postgres")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "admin123")
DB_NAME = os.getenv("DB_NAME", "jumptotech")

app = FastAPI(title=SERVICE)

REQUESTS = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["service", "path", "method"]
)


def get_conn():
    return psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS,
        cursor_factory=RealDictCursor,
    )


def init_db():
    conn = get_conn()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS courses (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            level TEXT NOT NULL,
            price TEXT NOT NULL,
            rating NUMERIC(2,1) NOT NULL
        )
    """)

    cur.execute("SELECT COUNT(*) AS count FROM courses")
    count = cur.fetchone()["count"]

    if count == 0:
        cur.execute("""
            INSERT INTO courses (title, author, level, price, rating)
            VALUES
            ('Docker & Kubernetes from Zero to Hero', 'JumpToTech', 'Beginner', '$19.99', 4.7),
            ('AWS for DevOps: Terraform + EKS + GitOps', 'JumpToTech', 'Intermediate', '$24.99', 4.8),
            ('CI/CD Masterclass: Jenkins to Argo CD', 'JumpToTech', 'All levels', '$17.99', 4.6),
            ('Python for Automation (DevOps Edition)', 'JumpToTech', 'Beginner', '$14.99', 4.5)
        """)

    conn.commit()
    cur.close()
    conn.close()


@app.on_event("startup")
def startup():
    init_db()


@app.middleware("http")
async def metrics_middleware(request, call_next):
    response = await call_next(request)
    REQUESTS.labels(service=SERVICE, path=request.url.path, method=request.method).inc()
    return response


@app.get("/health")
def health():
    return {"status": "ok", "service": SERVICE}


@app.get("/metrics")
def metrics():
    data = generate_latest()
    return PlainTextResponse(content=data.decode("utf-8"), media_type=CONTENT_TYPE_LATEST)


@app.get("/courses")
def get_courses():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, title, author, level, price, rating FROM courses ORDER BY id")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows