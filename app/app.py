import os
import random
import time

from flask import Flask, Response, jsonify, request
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

app = Flask(__name__)

REQUESTS = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "path", "status"]
)
LATENCY = Histogram(
    "http_request_duration_seconds", "HTTP request latency in seconds", ["path"]
)


def failure_rate() -> float:
    """Share of /work requests that fail on purpose (0.0 to 1.0).

    It is read on every request so it can be changed with the FAILURE_RATE
    environment variable, which the Helm chart sets from values.yaml.
    """
    try:
        return float(os.getenv("FAILURE_RATE", "0"))
    except ValueError:
        return 0.0


@app.before_request
def start_timer():
    request.environ["start_time"] = time.perf_counter()


@app.after_request
def record_metrics(response):
    path = request.url_rule.rule if request.url_rule else "unmatched"
    if path != "/metrics":
        elapsed = time.perf_counter() - request.environ.get("start_time", time.perf_counter())
        LATENCY.labels(path).observe(elapsed)
        REQUESTS.labels(request.method, path, str(response.status_code)).inc()
    return response


@app.route("/")
def index():
    return jsonify(service="demo-app", version=os.getenv("APP_VERSION", "dev"))


@app.route("/healthz")
def healthz():
    return jsonify(status="ok")


@app.route("/work")
def work():
    time.sleep(random.uniform(0.05, 0.3))
    if random.random() < failure_rate():
        return jsonify(error="simulated failure"), 500
    return jsonify(result="done")


@app.route("/metrics")
def metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)
