import psycopg2
import os
from fastapi import FastAPI

app = FastAPI(title="courses-service")

DB_HOST = os.getenv("DB_HOST", "postgres")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "admin123")
DB_NAME = os.getenv("DB_NAME", "jumptotech")

@app.get("/courses")
def get_courses():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    cur = conn.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS courses (id SERIAL PRIMARY KEY, name TEXT)")
    cur.execute("INSERT INTO courses (name) VALUES ('DevOps Bootcamp') RETURNING id")
    conn.commit()
    cur.execute("SELECT * FROM courses")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows