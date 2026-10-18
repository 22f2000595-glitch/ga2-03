
import os
import time
import uuid

from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
EMAIL = os.getenv("EMAIL", "").strip()
ALLOWED_ORIGIN = "https://dash-6rym3s.example.com"

app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_headers(request: Request, call_next):
    start = time.perf_counter()
    request_id = str(uuid.uuid4())
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = (
        f"{time.perf_counter() - start:.6f}"
    )
    return response

@app.get("/stats")
async def stats(values: str = Query(...)):
    if not EMAIL:
        raise HTTPException(500, "EMAIL is not configured")

    try:
        parts = values.split(",")
        if any(not part.strip() for part in parts):
            raise ValueError()
        numbers = [int(part.strip()) for part in parts]
    except ValueError:
        raise HTTPException(400, "values must be comma-separated integers")

    if not numbers:
        raise HTTPException(400, "At least one integer is required")

    total = sum(numbers)
    return {
        "email": EMAIL,
        "count": len(numbers),
        "sum": total,
        "min": min(numbers),
        "max": max(numbers),
        "mean": total / len(numbers),
    }
