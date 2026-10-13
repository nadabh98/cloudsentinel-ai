import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import classification_report
from sklearn.model_selection import train_test_split

FEATURES = ["cpu", "memory", "latency_ms", "http_errors"]

df = pd.read_csv("data.csv")
X_train, X_test, _, y_test = train_test_split(
    df[FEATURES], df["is_anomaly"], test_size=0.3, random_state=42, stratify=df["is_anomaly"]
)

model = IsolationForest(n_estimators=200, contamination=0.03, random_state=42)
model.fit(X_train)

pred = (model.predict(X_test) == -1).astype(int)
print(classification_report(y_test, pred, target_names=["normal", "anomalie"]))

joblib.dump(model, "models/isolation_forest.joblib")
print("Modèle sauvegardé.")
