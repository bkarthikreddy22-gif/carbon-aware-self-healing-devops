from fastapi.testclient import TestClient

from app.main import app, application_state

client = TestClient(app)


def reset_state():
    application_state.update({
        "status": "healthy",
        "failure_reason": None,
        "last_recovery_time": None,
        "failure_count": 0,
        "recovery_count": 0
    })


def test_home():
    reset_state()
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_health():
    reset_state()
    response = client.get("/health")
    assert response.status_code == 200


def test_failure_simulation():
    reset_state()
    response = client.post(
        "/simulate/failure",
        json={"reason": "Test failure"}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "failed"


def test_unhealthy_application():
    reset_state()

    client.post(
        "/simulate/failure",
        json={"reason": "Test failure"}
    )

    response = client.get("/health")
    assert response.status_code == 503


def test_recovery():
    reset_state()

    client.post(
        "/simulate/failure",
        json={"reason": "Test failure"}
    )

    response = client.post(
        "/simulate/recovery",
        json={"action": "manual_recovery"}
    )

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_metrics():
    reset_state()
    response = client.get("/metrics-data")

    assert response.status_code == 200
    assert "cpu_usage_percent" in response.json()
    assert "memory_usage_percent" in response.json()
