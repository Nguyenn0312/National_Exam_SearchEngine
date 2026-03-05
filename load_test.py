import asyncio
import time
from statistics import mean

import aiohttp  #pip install aiohttp

URL = "http://127.0.0.1:8000/search/math"
NB_REQUESTS = 1000
CONCURRENCY = 100
TIMEOUT_SECONDS = 60


def percentile(sorted_values, p):
    if not sorted_values:
        return None
    k = (len(sorted_values) - 1) * (p / 100.0)
    f = int(k)
    c = min(f + 1, len(sorted_values) - 1)
    if f == c:
        return float(sorted_values[f])
    return float(sorted_values[f] + (sorted_values[c] - sorted_values[f]) * (k - f))


async def one_request(session):
    start = time.perf_counter()
    try:
        async with session.get(URL) as resp:
            await resp.read()
            status = resp.status
            ok = 200 <= status < 400
    except Exception:
        ok = False
        status = None
    end = time.perf_counter()
    return end - start, ok, status


async def worker(worker_id, session, queue, results):
    while True:
        idx = await queue.get()
        if idx is None:
            queue.task_done()
            return
        latency_s, ok, status = await one_request(session)
        results[idx] = (latency_s, ok, status)
        queue.task_done()


async def run():
    timeout = aiohttp.ClientTimeout(total=TIMEOUT_SECONDS)
    connector = aiohttp.TCPConnector(limit=0, ttl_dns_cache=300)
    results = [None] * NB_REQUESTS
    queue = asyncio.Queue()

    for i in range(NB_REQUESTS):
        queue.put_nowait(i)

    async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
        workers = [asyncio.create_task(worker(i, session, queue, results)) for i in range(CONCURRENCY)]
        t0 = time.perf_counter()
        await queue.join()
        t1 = time.perf_counter()

        for _ in workers:
            queue.put_nowait(None)
        await asyncio.gather(*workers)

    total_s = t1 - t0
    latencies = [r[0] for r in results if r is not None]
    latencies_sorted = sorted(latencies)

    ok_count = sum(1 for r in results if r is not None and r[1])
    fail_count = NB_REQUESTS - ok_count

    p50 = percentile(latencies_sorted, 50)
    p95 = percentile(latencies_sorted, 95)
    p99 = percentile(latencies_sorted, 99)

    print(f"URL: {URL}")
    print(f"Requests: {NB_REQUESTS}")
    print(f"Concurrency: {CONCURRENCY}")
    print(f"Total wall time (s): {total_s:.6f}")
    print(f"RPS (approx): {NB_REQUESTS / total_s:.2f}")
    print(f"Success: {ok_count} | Fail: {fail_count}")
    print(f"Latency mean (ms): {mean(latencies) * 1000:.3f}")
    print(f"Latency p50 (ms): {p50 * 1000:.3f}")
    print(f"Latency p95 (ms): {p95 * 1000:.3f}")
    print(f"Latency p99 (ms): {p99 * 1000:.3f}")

    print("\nPer-request latencies (id, ms, ok, status):")
    for i, r in enumerate(results):
        latency_s, ok, status = r
        print(f"{i}\t{latency_s * 1000:.3f}\t{int(ok)}\t{status}")


if __name__ == "__main__":
    asyncio.run(run())
 
