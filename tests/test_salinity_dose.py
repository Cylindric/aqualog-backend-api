from fastapi.testclient import TestClient

from aqualog_api.app import create_app
from aqualog_api.config import Settings


def test_salinity_dose_returns_expected_quantity_in_success_envelope():
    app = create_app(Settings(app_env="test"))

    with TestClient(app) as client:
        response = client.get(
            "/api/v1/calculate/dose/salinity",
            params={"volume": 100.0, "current": 30.0, "target": 35.0},
            headers={"x-request-id": "req-salinity-1"},
        )

    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["request_id"] == "req-salinity-1"
    assert body["data"]["volume"] == 100.0
    assert body["data"]["current"] == 30.0
    assert body["data"]["target"] == 35.0
    assert body["data"]["quantity"] == 550.0


def test_salinity_dose_allows_negative_quantity_when_target_below_current():
    app = create_app(Settings(app_env="test"))

    with TestClient(app) as client:
        response = client.get(
            "/api/v1/calculate/dose/salinity",
            params={"volume": 10.0, "current": 35.0, "target": 30.0},
            headers={"x-request-id": "req-salinity-2"},
        )

    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["request_id"] == "req-salinity-2"
    assert body["data"]["quantity"] == -55.0


def test_salinity_dose_missing_or_invalid_params_return_standard_error_envelope():
    app = create_app(Settings(app_env="test"))

    with TestClient(app) as client:
        missing_response = client.get(
            "/api/v1/calculate/dose/salinity",
            params={"volume": 100.0, "current": 30.0},
            headers={"x-request-id": "req-salinity-missing"},
        )
        invalid_response = client.get(
            "/api/v1/calculate/dose/salinity",
            params={"volume": "bad", "current": 30.0, "target": 35.0},
            headers={"x-request-id": "req-salinity-invalid"},
        )

    missing_body = missing_response.json()
    invalid_body = invalid_response.json()

    assert missing_response.status_code == 422
    assert missing_body["success"] is False
    assert missing_body["error"]["code"] == "validation_error"
    assert missing_body["request_id"] == "req-salinity-missing"

    assert invalid_response.status_code == 422
    assert invalid_body["success"] is False
    assert invalid_body["error"]["code"] == "validation_error"
    assert invalid_body["request_id"] == "req-salinity-invalid"
