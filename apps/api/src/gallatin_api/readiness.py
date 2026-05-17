from typing import Literal

import psycopg
from pydantic import BaseModel


ReadinessState = Literal["ready", "unavailable"]


class DependencyStatus(BaseModel):
    name: str
    status: ReadinessState
    details: str


class ReadinessResponse(BaseModel):
    service: str
    status: ReadinessState
    dependencies: list[DependencyStatus]


def check_postgis(database_url: str) -> DependencyStatus:
    try:
        with psycopg.connect(database_url, connect_timeout=2) as connection:
            with connection.cursor() as cursor:
                cursor.execute("select postgis_full_version()")
                version = cursor.fetchone()
    except psycopg.Error as exc:
        return DependencyStatus(
            name="postgis",
            status="unavailable",
            details=f"PostGIS readiness check failed: {exc.__class__.__name__}: {exc}",
        )

    if not version or not version[0]:
        return DependencyStatus(
            name="postgis",
            status="unavailable",
            details="PostGIS readiness check returned no version information.",
        )

    return DependencyStatus(
        name="postgis",
        status="ready",
        details=str(version[0]),
    )
