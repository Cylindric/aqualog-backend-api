from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request, status
from pydantic import BaseModel, ConfigDict, field_validator
from sqlalchemy.orm import Session

from aqualog_api.aquarium_measurement_repository import (
    AquariumMeasurementRepository,
    DuplicateAquariumMeasurementError,
)
from aqualog_api.aquarium_repository import AquariumRepository
from aqualog_api.auth import get_current_user
from aqualog_api.db import get_session
from aqualog_api.models import AquariumMeasurement
from aqualog_api.responses import success_response
from aqualog_api.user_service import AuthenticatedUser

SUPPORTED_SALINITY_UNITS = {"ppt", "sg"}
SALINITY_PARAMETER = "salinity"
SG_TO_PPT_FACTOR = 1350.0
MAX_SALINITY_PPT = 100.0
MIN_SALINITY_SG = 1.0
MAX_SALINITY_SG = 1.04


class CreateSalinityMeasurementRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    unit: str
    value: float
    measured_at: datetime

    @field_validator("unit")
    @classmethod
    def validate_unit(cls, value: str) -> str:
        normalized = value.strip().lower()
        if normalized not in SUPPORTED_SALINITY_UNITS:
            raise ValueError("Salinity unit must be one of: ppt, sg")
        return normalized

    @field_validator("value")
    @classmethod
    def validate_value(cls, value: float, info) -> float:
        unit = (info.data.get("unit") or "").lower()
        if value <= 0:
            raise ValueError("Salinity value must be greater than 0")
        if unit == "ppt" and value > MAX_SALINITY_PPT:
            raise ValueError("Salinity value in ppt must be less than or equal to 100")
        if unit == "sg" and not (MIN_SALINITY_SG <= value <= MAX_SALINITY_SG):
            raise ValueError("Salinity value in sg must be between 1.0 and 1.04")
        return value

    @field_validator("measured_at")
    @classmethod
    def validate_timestamp(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("measured_at must include timezone information")
        return value


class SalinityMeasurementPayload(BaseModel):
    id: str
    aquarium_id: str
    parameter: str
    value: float
    unit: str
    raw_value: float
    raw_unit: str
    measured_at: str
    created_at: str


class SalinityMeasurementResponse(BaseModel):
    success: bool
    request_id: str
    data: SalinityMeasurementPayload


class SalinityMeasurementListResponse(BaseModel):
    success: bool
    request_id: str
    data: list[SalinityMeasurementPayload]


def _to_ppt(value: float, unit: str) -> float:
    if unit == "ppt":
        return value
    return (value - 1.0) * SG_TO_PPT_FACTOR


def _normalize_timestamp(value: datetime) -> datetime:
    return value.astimezone(timezone.utc).replace(microsecond=0)


def _to_utc_iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).isoformat()


def _to_payload(measurement: AquariumMeasurement) -> dict[str, str | float]:
    return {
        "id": measurement.id,
        "aquarium_id": measurement.aquarium_id,
        "parameter": measurement.parameter,
        "value": measurement.value,
        "unit": measurement.unit,
        "raw_value": measurement.raw_value,
        "raw_unit": measurement.raw_unit,
        "measured_at": _to_utc_iso(measurement.measured_at),
        "created_at": _to_utc_iso(measurement.created_at),
    }


def build_aquarium_measurement_router() -> APIRouter:
    router = APIRouter(prefix="/aquariums", tags=["aquarium-measurements"])

    @router.post(
        "/{aquarium_id}/measurements/salinity",
        response_model=SalinityMeasurementResponse,
        status_code=status.HTTP_201_CREATED,
    )
    async def create_salinity_measurement(
        aquarium_id: str,
        request: Request,
        payload: CreateSalinityMeasurementRequest = Body(...),
        current_user: AuthenticatedUser = Depends(get_current_user),
        session: Session = Depends(get_session),
    ):
        request_id = getattr(request.state, "request_id", "unknown")
        aquarium_repo = AquariumRepository(session)
        aquarium = aquarium_repo.get_by_id_and_owner(aquarium_id, current_user.user.id)
        if aquarium is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aquarium not found")

        measurement_repo = AquariumMeasurementRepository(session)
        normalized_measured_at = _normalize_timestamp(payload.measured_at)
        canonical_ppt = _to_ppt(payload.value, payload.unit)

        try:
            measurement = measurement_repo.create_salinity(
                aquarium_id=aquarium.id,
                owner_user_id=current_user.user.id,
                value_ppt=canonical_ppt,
                raw_value=payload.value,
                raw_unit=payload.unit,
                measured_at=normalized_measured_at,
            )
        except DuplicateAquariumMeasurementError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Duplicate salinity reading timestamp for aquarium",
            ) from exc

        return success_response(_to_payload(measurement), request_id=request_id, status_code=status.HTTP_201_CREATED)

    @router.get("/{aquarium_id}/measurements/salinity", response_model=SalinityMeasurementListResponse)
    async def list_salinity_measurements(
        aquarium_id: str,
        request: Request,
        measured_from: datetime | None = Query(default=None, alias="from"),
        measured_to: datetime | None = Query(default=None, alias="to"),
        current_user: AuthenticatedUser = Depends(get_current_user),
        session: Session = Depends(get_session),
    ):
        request_id = getattr(request.state, "request_id", "unknown")
        aquarium_repo = AquariumRepository(session)
        aquarium = aquarium_repo.get_by_id_and_owner(aquarium_id, current_user.user.id)
        if aquarium is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Aquarium not found")

        measurement_repo = AquariumMeasurementRepository(session)
        if measured_from is not None:
            measured_from = _normalize_timestamp(measured_from)
        if measured_to is not None:
            measured_to = _normalize_timestamp(measured_to)

        measurements = measurement_repo.list_salinity(
            aquarium_id=aquarium.id,
            owner_user_id=current_user.user.id,
            measured_from=measured_from,
            measured_to=measured_to,
        )
        return success_response([_to_payload(item) for item in measurements], request_id=request_id)

    return router
