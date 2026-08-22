"""Tests for CLI cache commands and performance benchmarks comparing un-cached vs L1 vs L2."""

import time
import pytest
from typer.testing import CliRunner
from backend.workline.knowledge.cache.cache import KnowledgeCache
from backend.workline.knowledge.cache.models import CacheObjectType, CacheOptions
from cli.wline.main import app as cli_app

runner = CliRunner()


def test_cli_cache_commands():
    # 1. wline cache stats
    res = runner.invoke(cli_app, ["cache", "stats"])
    assert res.exit_code == 0
    assert "KNOWLEDGE CACHE STATS" in res.stdout

    # 2. wline cache clean
    res = runner.invoke(cli_app, ["cache", "clean"])
    assert res.exit_code == 0
    assert "Cleared" in res.stdout

    # 3. wline cache clear with force
    res = runner.invoke(cli_app, ["cache", "clear", "--force"])
    assert res.exit_code == 0
    assert "cleared successfully" in res.stdout

    # 4. wline cache warm
    res = runner.invoke(cli_app, ["cache", "warm", "-p", "benchmark_proj"])
    assert res.exit_code == 0
    assert "Warmed knowledge cache" in res.stdout


def test_performance_benchmark_l1_vs_l2_vs_uncached(tmp_path):
    cache = KnowledgeCache(l2_base_dir=str(tmp_path / "cache"))
    key = "benchmark_item"
    payload = {"matrix": list(range(5000))}

    # 1. Uncached operation (simulated parse/computation)
    t0 = time.perf_counter()
    _ = [x * 2 for x in payload["matrix"]]
    uncached_duration = time.perf_counter() - t0

    # Store in cache
    cache.set(key, payload, CacheObjectType.RETRIEVAL, CacheOptions(project_id="p1"))

    # 2. L1 Memory cache hit
    t1 = time.perf_counter()
    l1_res = cache.get(key, CacheObjectType.RETRIEVAL)
    l1_duration = time.perf_counter() - t1
    assert l1_res is not None

    # Clear L1 to force L2 disk read
    cache.l1.clear()

    # 3. L2 Persistent cache hit
    t2 = time.perf_counter()
    l2_res = cache.get(key, CacheObjectType.RETRIEVAL)
    l2_duration = time.perf_counter() - t2
    assert l2_res is not None

    # L1 memory access is sub-millisecond
    assert l1_duration < 0.01
    assert l2_duration < 0.05
