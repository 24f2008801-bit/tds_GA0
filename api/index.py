from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import numpy as np

app = FastAPI()

# Proper CORS setup
aapp.add_middleware(

    CORSMiddleware,

    allow_origins=["*"],

    allow_credentials=False,

    allow_methods=["*"],

    allow_headers=["*"],


)

telemetry = [
    {"region": "emea", "latency_ms": 120, "uptime": 99.9},
    {"region": "emea", "latency_ms": 180, "uptime": 99.5},
    {"region": "emea", "latency_ms": 160, "uptime": 99.7},
    {"region": "amer", "latency_ms": 140, "uptime": 99.8},
    {"region": "amer", "latency_ms": 170, "uptime": 99.6},
    {"region": "amer", "latency_ms": 155, "uptime": 99.4},
]

class MetricsRequest(BaseModel):
    regions: list[str]
    threshold_ms: int

@app.options("/")
async def options_handler():
    return {"ok": True}

@app.post("/")
async def get_metrics(data: MetricsRequest):
    result = {}

    for region in data.regions:
        rows = [r for r in telemetry if r["region"] == region]

        if not rows:
            continue

        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime"] for r in rows]

        result[region] = {
            "avg_latency": round(sum(latencies) / len(latencies), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 2),
            "breaches": sum(1 for x in latencies if x > data.threshold_ms)
        }

    return result