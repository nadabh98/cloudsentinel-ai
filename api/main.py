import logging
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI
from google.cloud import bigquery
from pydantic import BaseModel, Field

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("cloudsentinel")

FEATURES = ["cpu", "memory", "latency_ms", "http_errors"]
MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "isolation_forest.joblib"

app = FastAPI(title="CloudSentinel AI", version="0.2.0")
model = joblib.load(MODEL_PATH)

bq = bigquery.Client()
TABLE_ID = f"{bq.project}.cloudsentinel.predictions"


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

    row = {
        "ts": datetime.now(timezone.utc).isoformat(),
        **m.model_dump(),
        "is_anomaly": is_anomaly,
        "anomaly_score": score,
    }
    try:
        errors = bq.insert_rows_json(TABLE_ID, [row])
        if errors:
            logger.error("BigQuery insert errors: %s", errors)
    except Exception:
        logger.exception("BigQuery insert failed")

    return {"is_anomaly": is_anomaly, "anomaly_score": round(score, 4)}
