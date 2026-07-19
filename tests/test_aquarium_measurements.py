from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from aqualog_api.app import create_app
from aqualog_api.config import Settings


@pytest.fixture
def auth_settings(tmp_path):
    return Settings(
        app_env="test",
        oauth_issuer_url="https://auth.example.com/application/o/aqualog",
        oauth_audience="test-client-id",
        test_database_url=f"sqlite+pysqlite:///{tmp_path}/test-aquarium-measurements.db",
    )


def _auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}", "x-request-id": "req-measure"}


def _create_aquarium(client: TestClient, token: str) -> str:
    response = client.post(
        "/api/v1/aquariums",
        headers=_auth_header(token),
        json={"name": "Display Reef", "type": "reef", "volume": {"value": 200.0, "unit": "L"}},
    )
    assert response.status_code == 201
    return response.json()["data"]["id"]


def test_salinity_measurements_require_authentication(auth_settings):
    app = create_app(auth_settings)

    with TestClient(app) as client:
        assert client.post(
            "/api/v1/aquariums/aq-1/measurements/salinity",
            json={"unit": "ppt", "value": 35.0, "measured_at": "2026-07-01T12:00:00Z"},
        ).status_code == 401
        assert client.get("/api/v1/aquariums/aq-1/measurements/salinity").status_code == 401


def test_salinity_measurement_create_list_happy_path(create_valid_token, auth_settings, mock_jwks):
    token = create_valid_token(sub="measure-owner", aud="test-client-id")
    app = create_app(auth_settings)

    with patch("aqualog_api.auth.get_jwks_keys") as mock_get_keys:
        mock_get_keys.return_value = mock_jwks
        with TestClient(app) as client:
            aquarium_id = _create_aquarium(client, token)

            create_response = client.post(
                f"/api/v1/aquariums/{aquarium_id}/measurements/salinity",
                headers=_auth_header(token),
                json={"unit": "sg", "value": 1.026, "measured_at": "2026-07-01T12:00:00.987654Z"},
            )
            assert create_response.status_code == 201
            created = create_response.json()["data"]
            assert created["parameter"] == "salinity"
            assert created["unit"] == "ppt"
            assert created["value"] == pytest.approx(35.1)
            assert created["raw_unit"] == "sg"
            assert created["raw_value"] == pytest.approx(1.026)
            assert created["measured_at"].endswith("+00:00")
            assert "." not in created["measured_at"]

            second_response = client.post(
                f"/api/v1/aquariums/{aquarium_id}/measurements/salinity",
                headers=_auth_header(token),
                json={"unit": "ppt", "value": 35.5, "measured_at": "2026-07-01T12:05:00Z"},
            )
            assert second_response.status_code == 201

            list_response = client.get(
                f"/api/v1/aquariums/{aquarium_id}/measurements/salinity",
                headers=_auth_header(token),
            )
            assert list_response.status_code == 200
            payload = list_response.json()
            assert isinstance(payload["data"], list)
            assert "pagination" not in payload
            assert [item["measured_at"] for item in payload["data"]] == [
                "2026-07-01T12:00:00+00:00",
                "2026-07-01T12:05:00+00:00",
            ]

            filtered = client.get(
                f"/api/v1/aquariums/{aquarium_id}/measurements/salinity",
                headers=_auth_header(token),
                params={"from": "2026-07-01T12:01:00Z"},
            )
            assert filtered.status_code == 200
            assert len(filtered.json()["data"]) == 1
            assert filtered.json()["data"][0]["measured_at"] == "2026-07-01T12:05:00+00:00"


def test_salinity_measurement_duplicate_timestamp_and_cross_user(create_valid_token, auth_settings, mock_jwks):
    owner_token = create_valid_token(sub="owner", aud="test-client-id")
    other_token = create_valid_token(sub="other", aud="test-client-id")
    app = create_app(auth_settings)

    with patch("aqualog_api.auth.get_jwks_keys") as mock_get_keys:
        mock_get_keys.return_value = mock_jwks
        with TestClient(app) as client:
            aquarium_id = _create_aquarium(client, owner_token)

            created = client.post(
                f"/api/v1/aquariums/{aquarium_id}/measurements/salinity",
                headers=_auth_header(owner_token),
                json={"unit": "ppt", "value": 35.0, "measured_at": "2026-07-01T12:00:00.950000Z"},
            )
            assert created.status_code == 201

            duplicate = client.post(
                f"/api/v1/aquariums/{aquarium_id}/measurements/salinity",
                headers=_auth_header(owner_token),
                json={"unit": "sg", "value": 1.026, "measured_at": "2026-07-01T12:00:00.100000Z"},
            )
            assert duplicate.status_code == 409

            assert client.post(
                f"/api/v1/aquariums/{aquarium_id}/measurements/salinity",
                headers=_auth_header(other_token),
                json={"unit": "ppt", "value": 35.0, "measured_at": "2026-07-01T12:01:00Z"},
            ).status_code == 404

            assert client.get(
                f"/api/v1/aquariums/{aquarium_id}/measurements/salinity",
                headers=_auth_header(other_token),
            ).status_code == 404


def test_salinity_measurement_validation_errors(create_valid_token, auth_settings, mock_jwks):
    token = create_valid_token(sub="validator", aud="test-client-id")
    app = create_app(auth_settings)

    with patch("aqualog_api.auth.get_jwks_keys") as mock_get_keys:
        mock_get_keys.return_value = mock_jwks
        with TestClient(app) as client:
            aquarium_id = _create_aquarium(client, token)

            unsupported_unit = client.post(
                f"/api/v1/aquariums/{aquarium_id}/measurements/salinity",
                headers=_auth_header(token),
                json={"unit": "psu", "value": 35.0, "measured_at": "2026-07-01T12:00:00Z"},
            )
            assert unsupported_unit.status_code == 422

            invalid_sg = client.post(
                f"/api/v1/aquariums/{aquarium_id}/measurements/salinity",
                headers=_auth_header(token),
                json={"unit": "sg", "value": 1.2, "measured_at": "2026-07-01T12:00:00Z"},
            )
            assert invalid_sg.status_code == 422

            missing_field = client.post(
                f"/api/v1/aquariums/{aquarium_id}/measurements/salinity",
                headers=_auth_header(token),
                json={"unit": "ppt", "value": 35.0},
            )
            assert missing_field.status_code == 422

            missing_timezone = client.post(
                f"/api/v1/aquariums/{aquarium_id}/measurements/salinity",
                headers=_auth_header(token),
                json={"unit": "ppt", "value": 35.0, "measured_at": "2026-07-01T12:00:00"},
            )
            assert missing_timezone.status_code == 422
