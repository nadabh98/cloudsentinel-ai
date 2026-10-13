import logging
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cloudsentinel")

FEATURES = ["cpu", "memory", "latency_ms", "http_errors"]
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "isolation_forest.joblib"

app = FastAPI(title="CloudSentinel AI", version="0.1.0")
model = joblib.load(MODEL_PATH)


class Metrics(BaseModel):
    cpu: float = Field(..., ge=0, le=100, description="CPU usage (%)")
    memory: float = Field(..., ge=0, le=100, description="Memory usage (%)")
    latency_ms: float = Field(..., ge=0, description="Response time (ms)")
    http_errors: float = Field(..., ge=0, description="HTTP errors per minute")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/predict")
def predict(m: Metrics):
    X = pd.DataFrame([m.model_dump()])[FEATURES]
    is_anomaly = bool(model.predict(X)[0] == -1)
    score = float(model.decision_function(X)[0])
    logger.info("prediction anomaly=%s score=%.4f input=%s", is_anomaly, score, m.model_dump())
    return {"is_anomaly": is_anomaly, "anomaly_score": round(score, 4)}
