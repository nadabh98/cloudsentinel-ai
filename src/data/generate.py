import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
n = 5000

df = pd.DataFrame({
    "timestamp": pd.date_range("2026-01-01", periods=n, freq="min"),
    "cpu": rng.normal(45, 8, n),
    "memory": rng.normal(60, 7, n),
    "latency_ms": rng.normal(120, 20, n),
    "http_errors": rng.poisson(2, n).astype(float),
})
df["is_anomaly"] = 0

idx = rng.choice(n, int(0.03 * n), replace=False)
severity = rng.uniform(0.3, 1.0, len(idx))   # 30 % à 100 % de l'incident complet
df.loc[idx, "cpu"] += severity * rng.uniform(15, 40, len(idx))
df.loc[idx, "latency_ms"] *= 1 + severity * rng.uniform(0.5, 3, len(idx))
df.loc[idx, "http_errors"] += rng.poisson(severity * 12)
df.loc[idx, "is_anomaly"] = 1

df["cpu"] = df["cpu"].clip(0, 100)
df["memory"] = df["memory"].clip(0, 100)
df.to_csv("data.csv", index=False)
print(df.is_anomaly.value_counts())
