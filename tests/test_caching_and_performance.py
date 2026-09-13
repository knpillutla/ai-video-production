"""Tests for enterprise caching layer, SHA-256 prompt hashing, and high-throughput concurrency."""

import asyncio
import time
import pytest

from src.core.cache import AsyncCacheManager, cache, cached


@pytest.mark.asyncio
async def test_cache_set_get_and_expiration():
    """Verify basic caching, retrieval, and TTL expiration."""
    test_cache = AsyncCacheManager(max_size=100, default_ttl=2)

    # Set and get
    await test_cache.set("key1", {"data": "video_script_01"}, ttl=1)
    cached_val = await test_cache.get("key1")
    assert cached_val == {"data": "video_script_01"}

    # Stats tracking
    stats = await test_cache.get_stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 0
    assert stats["size"] == 1

    # Wait for expiration
    await asyncio.sleep(1.1)
    expired_val = await test_cache.get("key1")
    assert expired_val is None

    stats_after = await test_cache.get_stats()
    assert stats_after["misses"] == 1
    assert stats_after["evictions"] >= 1


@pytest.mark.asyncio
async def test_sha256_prompt_hashing_consistency():
    """Verify deterministic SHA-256 prompt and payload hashing."""
    prompt_a = "Generate 4K dramatic lighting for Telugu comedy scene 1"
    prompt_b = "Generate 4K dramatic lighting for Telugu comedy scene 1"
    prompt_c = "Generate 4K dramatic lighting for Telugu comedy scene 2"

    hash_a = AsyncCacheManager.compute_hash(prompt_a)
    hash_b = AsyncCacheManager.compute_hash(prompt_b)
    hash_c = AsyncCacheManager.compute_hash(prompt_c)

    assert hash_a == hash_b
    assert hash_a != hash_c
    assert len(hash_a) == 64  # Hex-encoded SHA-256


@pytest.mark.asyncio
async def test_high_concurrency_cache_throughput():
    """Simulate high concurrency with 100 parallel readers and writers for millions of users."""
    test_cache = AsyncCacheManager(max_size=500, default_ttl=60)

    async def writer(task_id: int):
        for i in range(20):
            await test_cache.set(f"channel_stats_{task_id % 10}", {"views": i * 1000})
            await asyncio.sleep(0.001)

    async def reader(task_id: int):
        hits = 0
        for _ in range(20):
            res = await test_cache.get(f"channel_stats_{task_id % 10}")
            if res is not None:
                hits += 1
            await asyncio.sleep(0.001)
        return hits

    tasks = []
    # 50 writers and 50 readers concurrently
    for i in range(50):
        tasks.append(asyncio.create_task(writer(i)))
        tasks.append(asyncio.create_task(reader(i)))

    results = await asyncio.gather(*tasks)
    stats = await test_cache.get_stats()
    assert stats["size"] <= 500
    assert stats["hits"] + stats["misses"] > 0


@pytest.mark.asyncio
async def test_cached_decorator_behavior():
    """Verify @cached decorator skips execution on cache hit."""
    call_counter = 0

    @cached(ttl_seconds=10, namespace="test_analytics")
    async def expensive_analytics_calculation(channel_id: str) -> dict:
        nonlocal call_counter
        call_counter += 1
        return {"channel_id": channel_id, "computed_revenue": 1420.50}

    # First call - cache miss, runs function
    res1 = await expensive_analytics_calculation("channel_alpha")
    assert res1["computed_revenue"] == 1420.50
    assert call_counter == 1

    # Second call - cache hit, does not run function
    res2 = await expensive_analytics_calculation("channel_alpha")
    assert res2["computed_revenue"] == 1420.50
    assert call_counter == 1

    # Different argument - cache miss, runs function
    res3 = await expensive_analytics_calculation("channel_beta")
    assert res3["channel_id"] == "channel_beta"
    assert call_counter == 2
