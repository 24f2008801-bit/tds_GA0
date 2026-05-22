from fastapi import FastAPI, Response
from pydantic import BaseModel
import numpy as np
import json
from pathlib import Path

app = FastAPI()

# Load telemetry data
data_path = Path(__file__).parent.parent / "q-vercel-latency.json"

with open(data_path, "r") as f:
    telemetry = json.load(f)

class RequestBody(BaseModel):
    regions: list[str]
    threshold_ms: int

def add_cors_headers(response: Response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"

@app.get("/api/index")
def home(response: Response):
    add_cors_headers(response)
    return {"status": "ok"}

@app.options("/api/index")
def options_handler(response: Response):
    add_cors_headers(response)
    return {"ok": True}

@app.post("/api/index")
def metrics(data: RequestBody, response: Response):
    add_cors_headers(response)

    result = {}

    for region in data.regions:
        rows = [r for r in telemetry if r["region"] == region]

        if not rows:
            continue

        latencies = [r["latency_ms"] for r in rows]
        uptimes = [r["uptime_pct"] for r in rows]

        result[region] = {
            "avg_latency": round(sum(latencies) / len(latencies), 2),
            "p95_latency": round(float(np.percentile(latencies, 95)), 2),
            "avg_uptime": round(sum(uptimes) / len(uptimes), 3),
            "breaches": sum(1 for x in latencies if x > data.threshold_ms)
        }

    return result

handler = app
