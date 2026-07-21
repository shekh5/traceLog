"""HTTP-level checks for the optional service bearer boundary."""

import pytest
from fastapi.testclient import TestClient

from dashboard.main import app as dashboard_app
from patient.agent import app as patient_app
from tracelog.config import get_settings


@pytest.fixture
def protected_offline_services():
    settings = get_settings()
    old_key = settings.service_api_key
    old_offline = settings.offline_demo_mode
    settings.service_api_key = "route-test-secret"
    settings.offline_demo_mode = True
    try:
        yield
    finally:
        settings.service_api_key = old_key
        settings.offline_demo_mode = old_offline


def test_sensitive_dashboard_routes_require_bearer(protected_offline_services):
    with TestClient(dashboard_app) as client:
        assert client.post("/ask", json={"message": "hello"}).status_code == 401
        assert client.post("/selfeval").status_code == 401
        assert client.get("/healthz").status_code == 200
        assert client.get("/healthz").json()["auth_required"] is True


def test_dashboard_routes_accept_valid_bearer(protected_offline_services):
    headers = {"Authorization": "Bearer route-test-secret"}
    with TestClient(dashboard_app) as client:
        ask = client.post("/ask", json={"message": "hello"}, headers=headers)
        assert ask.status_code == 200
        assert ask.json()["demo_mode"] == "offline_fixture"
        score = client.post("/selfeval", headers=headers)
        assert score.status_code == 200
        assert score.json()["fixture"] is True


def test_patient_chat_rejects_missing_or_wrong_bearer(protected_offline_services):
    with TestClient(patient_app) as client:
        payload = {"message": "hello"}
        assert client.post("/chat", json=payload).status_code == 401
        wrong = client.post(
            "/chat", json=payload, headers={"Authorization": "Bearer wrong"}
        )
        assert wrong.status_code == 401
        assert client.get("/healthz").status_code == 200
