import pytest
from unittest.mock import AsyncMock, patch

from app.infrastructure.services.cache_service import RedisCacheService


@pytest.mark.asyncio
async def test_cache_service_disconnected():
    cache = RedisCacheService(redis_url=None)
    assert not cache.is_connected
    assert await cache.get_json("key") is None
    assert await cache.set_json("key", {"a": 1}) is False
    assert await cache.delete("key") is False
    assert await cache.delete_pattern("key*") is False


@pytest.mark.asyncio
async def test_cache_service_operations():
    cache = RedisCacheService(redis_url="redis://localhost:6379/0")
    
    mock_client = AsyncMock()
    mock_client.get.return_value = '{"foo": "bar"}'
    mock_client.set.return_value = True
    mock_client.delete.return_value = True
    mock_client.keys.return_value = ["products:1", "products:2"]
    
    cache._client = mock_client
    assert cache.is_connected

    # Get
    res = await cache.get_json("products:1")
    assert res == {"foo": "bar"}
    mock_client.get.assert_called_once_with("products:1")

    # Set
    success = await cache.set_json("products:1", {"foo": "bar"}, ttl=100)
    assert success is True
    mock_client.set.assert_called_once_with("products:1", '{"foo": "bar"}', ex=100)

    # Delete
    deleted = await cache.delete("products:1")
    assert deleted is True
    mock_client.delete.assert_called_with("products:1")

    # Delete pattern
    pattern_deleted = await cache.delete_pattern("products:*")
    assert pattern_deleted is True
    mock_client.keys.assert_called_once_with("products:*")
    mock_client.delete.assert_called_with("products:1", "products:2")

    # Close
    await cache.close()
    mock_client.aclose.assert_called_once()
    assert not cache.is_connected
