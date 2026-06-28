from __future__ import annotations

import asyncio

import pytest

from runpod_inference_lab.runners.concurrency import run_with_concurrency_limit


@pytest.mark.asyncio
async def test_run_with_concurrency_limit_respects_limit():
    active = 0
    max_active = 0

    async def worker(index: int, item: int) -> int:
        nonlocal active, max_active
        active += 1
        max_active = max(max_active, active)
        await asyncio.sleep(0.01)
        active -= 1
        return index + item

    results = await run_with_concurrency_limit([1, 1, 1, 1, 1], concurrency=2, worker=worker)

    assert results == [1, 2, 3, 4, 5]
    assert max_active <= 2
