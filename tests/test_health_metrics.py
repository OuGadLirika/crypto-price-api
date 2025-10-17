import pytest
from unittest.mock import AsyncMock, Mock
from aiohttp import web

from app.controllers.health_controller import HealthController
from app.controllers.metrics_controller import MetricsController
from app.services.metrics_service import MetricsService


@pytest.mark.asyncio
async def test_health_check_success():
    """Test health endpoint returns ok when database is connected."""
    mock_session = AsyncMock()
    mock_result = Mock()
    mock_result.scalar_one.return_value = 1
    mock_session.execute.return_value = mock_result
    
    mock_session_factory = Mock(return_value=mock_session)
    mock_session_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session_factory.return_value.__aexit__ = AsyncMock(return_value=None)
    
    controller = HealthController(mock_session_factory)
    request = Mock(spec=web.Request)
    
    response = await controller.check(request)
    
    assert response.status == 200
    data = response.body
    assert b"ok" in data
    assert b"database" in data
    assert b"connected" in data


@pytest.mark.asyncio
async def test_health_check_database_error():
    """Test health endpoint returns 503 when database fails."""
    mock_session = AsyncMock()
    mock_session.execute.side_effect = Exception("Database connection failed")
    
    mock_session_factory = Mock(return_value=mock_session)
    mock_session_factory.return_value.__aenter__ = AsyncMock(return_value=mock_session)
    mock_session_factory.return_value.__aexit__ = AsyncMock(return_value=None)
    
    controller = HealthController(mock_session_factory)
    request = Mock(spec=web.Request)
    
    response = await controller.check(request)
    
    assert response.status == 503
    data = response.body
    assert b"degraded" in data


@pytest.mark.asyncio
async def test_metrics_initial_state():
    """Test metrics endpoint returns initial state."""
    metrics_service = MetricsService()
    controller = MetricsController(metrics_service)
    request = Mock(spec=web.Request)
    
    response = await controller.get_metrics(request)
    
    assert response.status == 200
    data = response.body
    assert b"uptime_seconds" in data
    assert b"requests_total" in data
    assert b"errors_total" in data
    assert b"success_rate" in data


@pytest.mark.asyncio
async def test_metrics_service_counts_requests():
    """Test metrics service correctly counts requests."""
    metrics_service = MetricsService()
    
    metrics_service.increment_request_count()
    metrics_service.increment_request_count()
    metrics_service.increment_request_count()
    
    metrics = metrics_service.get_metrics()
    
    assert metrics["requests_total"] == 3
    assert metrics["errors_total"] == 0
    assert metrics["success_rate"] == 100.0


@pytest.mark.asyncio
async def test_metrics_service_counts_errors():
    """Test metrics service correctly counts errors."""
    metrics_service = MetricsService()
    
    metrics_service.increment_request_count()
    metrics_service.increment_request_count()
    metrics_service.increment_request_count()
    metrics_service.increment_error_count()
    
    metrics = metrics_service.get_metrics()
    
    assert metrics["requests_total"] == 3
    assert metrics["errors_total"] == 1
    assert metrics["success_rate"] == pytest.approx(66.666, rel=0.01)


@pytest.mark.asyncio
async def test_metrics_service_success_rate_zero_requests():
    """Test metrics service handles zero requests correctly."""
    metrics_service = MetricsService()
    
    metrics = metrics_service.get_metrics()
    
    assert metrics["requests_total"] == 0
    assert metrics["errors_total"] == 0
    assert metrics["success_rate"] == 100.0


@pytest.mark.asyncio
async def test_metrics_service_uptime():
    """Test metrics service tracks uptime."""
    import time
    
    metrics_service = MetricsService()
    time.sleep(0.1)
    
    metrics = metrics_service.get_metrics()
    
    assert metrics["uptime_seconds"] >= 0
    assert isinstance(metrics["uptime_seconds"], int)
