import app as app_module


def client():
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client()


def test_healthz():
    response = client().get("/healthz")
    assert response.status_code == 200
    assert response.get_json()["status"] == "ok"


def test_work_succeeds_when_failure_rate_is_zero(monkeypatch):
    monkeypatch.setenv("FAILURE_RATE", "0")
    response = client().get("/work")
    assert response.status_code == 200


def test_work_fails_when_failure_rate_is_one(monkeypatch):
    monkeypatch.setenv("FAILURE_RATE", "1")
    response = client().get("/work")
    assert response.status_code == 500


def test_metrics_exposes_request_counter(monkeypatch):
    monkeypatch.setenv("FAILURE_RATE", "0")
    c = client()
    c.get("/work")
    body = c.get("/metrics").get_data(as_text=True)
    assert "http_requests_total" in body
    assert 'path="/work"' in body


def test_tracing_is_off_without_endpoint(monkeypatch):
    from flask import Flask

    import tracing

    monkeypatch.delenv("OTEL_EXPORTER_OTLP_ENDPOINT", raising=False)
    assert tracing.setup_tracing(Flask("off")) is False


def test_tracing_records_a_span_for_work_but_not_for_healthz(monkeypatch):
    from flask import Flask
    from opentelemetry.sdk.trace.export.in_memory_span_exporter import InMemorySpanExporter

    import tracing

    monkeypatch.setenv("FAILURE_RATE", "0")
    exporter = InMemorySpanExporter()
    traced = Flask("traced")

    @traced.route("/work")
    def work():
        return "ok"

    @traced.route("/healthz")
    def healthz():
        return "ok"

    assert tracing.setup_tracing(traced, exporter=exporter) is True
    c = traced.test_client()
    c.get("/work")
    c.get("/healthz")
    names = [span.name for span in exporter.get_finished_spans()]
    assert any("/work" in n for n in names)
    assert not any("healthz" in n for n in names)
