from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from aqualog_api.aquarium_measurement_repository import (
    AquariumMeasurementRepository,
    DuplicateAquariumMeasurementError,
)
from aqualog_api.aquarium_repository import AquariumRepository
from aqualog_api.db import Base
from aqualog_api.user_repository import UserRepository


def _build_repos(tmp_path):
    engine = create_engine(f"sqlite+pysqlite:///{tmp_path}/aquarium-measurement-repo-test.db", future=True)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, future=True, expire_on_commit=False)()
    return AquariumRepository(session), AquariumMeasurementRepository(session), UserRepository(session), session


def test_measurement_repository_create_list_and_filters(tmp_path):
    aquarium_repo, measurement_repo, user_repo, _ = _build_repos(tmp_path)
    owner = user_repo.resolve_or_create("https://issuer.example.com", "owner")
    other = user_repo.resolve_or_create("https://issuer.example.com", "other")

    aquarium = aquarium_repo.create(
        owner_user_id=owner.id,
        name="Display",
        aquarium_type="reef",
        volume_liters=120.0,
    )

    m1 = measurement_repo.create_salinity(
        aquarium_id=aquarium.id,
        owner_user_id=owner.id,
        value_ppt=34.8,
        raw_value=1.026,
        raw_unit="sg",
        measured_at=datetime(2026, 7, 1, 12, 0, 0, tzinfo=timezone.utc),
    )
    m2 = measurement_repo.create_salinity(
        aquarium_id=aquarium.id,
        owner_user_id=owner.id,
        value_ppt=35.0,
        raw_value=35.0,
        raw_unit="ppt",
        measured_at=datetime(2026, 7, 1, 12, 5, 0, tzinfo=timezone.utc),
    )

    all_rows = measurement_repo.list_salinity(aquarium.id, owner.id)
    assert [m.id for m in all_rows] == [m1.id, m2.id]
    assert all_rows[0].raw_value == 1.026
    assert all_rows[0].raw_unit == "sg"
    assert all_rows[1].unit == "ppt"

    filtered_rows = measurement_repo.list_salinity(
        aquarium.id,
        owner.id,
        measured_from=datetime(2026, 7, 1, 12, 1, 0, tzinfo=timezone.utc),
    )
    assert [m.id for m in filtered_rows] == [m2.id]

    try:
        measurement_repo.list_salinity(aquarium.id, other.id)
        assert False, "Expected ValueError"
    except ValueError:
        pass


def test_measurement_repository_rejects_duplicate_timestamp(tmp_path):
    aquarium_repo, measurement_repo, user_repo, _ = _build_repos(tmp_path)
    owner = user_repo.resolve_or_create("https://issuer.example.com", "owner")
    aquarium = aquarium_repo.create(
        owner_user_id=owner.id,
        name="Nano",
        aquarium_type="reef",
        volume_liters=80.0,
    )
    measured_at = datetime(2026, 7, 1, 12, 0, 0, tzinfo=timezone.utc)

    measurement_repo.create_salinity(
        aquarium_id=aquarium.id,
        owner_user_id=owner.id,
        value_ppt=35.0,
        raw_value=35.0,
        raw_unit="ppt",
        measured_at=measured_at,
    )

    try:
        measurement_repo.create_salinity(
            aquarium_id=aquarium.id,
            owner_user_id=owner.id,
            value_ppt=35.1,
            raw_value=1.026,
            raw_unit="sg",
            measured_at=measured_at,
        )
        assert False, "Expected DuplicateAquariumMeasurementError"
    except DuplicateAquariumMeasurementError:
        pass
