"""Integration tests for health endpoints."""

import pytest
from unittest.mock import patch


@pytest.mark.asyncio
async def test_ping(client):
    response = await client.get("/api/v1/ping")
    assert response.status_code == 200
    assert response.json() == {"ping": "pong"}


@pytest.mark.asyncio
async def test_health_check_structure(client):
    with (
        patch("app.api.v1.endpoints.health.check_db_connection", return_value=True),
        patch("app.api.v1.endpoints.health.check_redis_connection", return_value=True),
    ):
        response = await client.get("/api/v1/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert "components" in body
    assert body["components"]["database"]["status"] == "ok"
    assert body["components"]["cache"]["status"] == "ok"


@pytest.mark.asyncio
async def test_health_degraded_when_db_down(client):
    with (
        patch("app.api.v1.endpoints.health.check_db_connection", return_value=False),
        patch("app.api.v1.endpoints.health.check_redis_connection", return_value=True),
    ):
        response = await client.get("/api/v1/health")
    assert response.json()["status"] == "degraded"
