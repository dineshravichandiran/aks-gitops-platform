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
