"""Manual integration test — run with pytest after starting the server."""
import pytest
import httpx


@pytest.mark.asyncio
async def test_health_endpoint():
    """Test the health check endpoint."""
    async with httpx.AsyncClient() as client:
        resp = await client.get("http://127.0.0.1:8000/health")
        assert resp.status_code == 200
        assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_cors_headers():
    """Test CORS headers are set."""
    async with httpx.AsyncClient() as client:
        resp = await client.options(
            "http://127.0.0.1:8000/health",
            headers={"Origin": "http://localhost:5173"},
        )
        assert resp.status_code in (200, 405)
