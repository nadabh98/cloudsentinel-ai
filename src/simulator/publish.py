import json
import random
import subprocess
import sys

N = int(sys.argv[1]) if len(sys.argv) > 1 else 200
TOPIC = "metrics-stream"

for i in range(N):
    if random.random() < 0.05:  # incident
        m = {
            "cpu": round(min(100, random.uniform(80, 99)), 1),
            "memory": round(min(100, random.uniform(75, 95)), 1),
            "latency_ms": round(random.uniform(350, 700), 1),
            "http_errors": round(random.uniform(15, 45)),
        }
    else:  # normal
        m = {
            "cpu": round(min(100, max(0, random.gauss(45, 8))), 1),
            "memory": round(min(100, max(0, random.gauss(60, 7))), 1),
            "latency_ms": round(max(0, random.gauss(120, 20)), 1),
            "http_errors": max(0, round(random.gauss(2, 1.5))),
        }
    subprocess.run(
        ["gcloud", "pubsub", "topics", "publish", TOPIC, "--message", json.dumps(m)],
        capture_output=True,
    )
    print(i + 1, m)
