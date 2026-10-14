import os
import joblib
import pandas as pd
from google.cloud import storage
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

BUCKET = os.environ.get("BUCKET", "cloudsentinel-ai-511522-artifacts")
FEATURES = ["cpu", "memory", "latency_ms", "http_errors"]

client = storage.Client()
bucket = client.bucket(BUCKET)
bucket.blob("data/data.csv").download_to_filename("/tmp/data.csv")

df = pd.read_csv("/tmp/data.csv")
X_train, X_test, _, y_test = train_test_split(
    df[FEATURES], df["is_anomaly"], test_size=0.3, random_state=42, stratify=df["is_anomaly"]
)

model = IsolationForest(n_estimators=200, contamination=0.03, random_state=42)
model.fit(X_train)

pred = (model.predict(X_test) == -1).astype(int)
print(classification_report(y_test, pred, target_names=["normal", "anomalie"]))

joblib.dump(model, "/tmp/model.joblib")
bucket.blob("vertex-model/model.joblib").upload_from_filename("/tmp/model.joblib")
print("Model uploaded to gs://%s/vertex-model/model.joblib" % BUCKET)
