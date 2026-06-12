#!/usr/bin/env python3
"""Hit mock microservice endpoints to generate simulated failures."""

import asyncio
import os
import random

import httpx

SERVICE_A = os.getenv("SERVICE_A_URL", "http://localhost:8001")
SERVICE_B = os.getenv("SERVICE_B_URL", "http://localhost:8002")
SERVICE_C = os.getenv("SERVICE_C_URL", "http://localhost:8003")
INTERVAL = int(os.getenv("SIMULATOR_INTERVAL", "10"))

REQUESTS = [
    ("GET", f"{SERVICE_A}/api/users/1"),
    ("POST", f"{SERVICE_A}/api/users/login"),
    ("GET", f"{SERVICE_A}/api/config"),
    ("GET", f"{SERVICE_A}/api/profile"),
    ("GET", f"{SERVICE_B}/api/orders/42"),
    ("POST", f"{SERVICE_B}/api/orders"),
    ("GET", f"{SERVICE_B}/api/inventory"),
    ("GET", f"{SERVICE_B}/api/reports"),
    ("GET", f"{SERVICE_C}/api/payments/pay-1"),
    ("POST", f"{SERVICE_C}/api/payments/charge"),
    ("GET", f"{SERVICE_C}/api/notifications"),
    ("GET", f"{SERVICE_C}/api/external/status"),
]


async def hit_endpoint(client: httpx.AsyncClient, method: str, url: str) -> None:
    try:
        if method == "GET":
            await client.get(url)
        else:
            await client.post(url, json={"token": "test", "amount": 10})
    except Exception:
        pass


async def run_cycle() -> None:
    async with httpx.AsyncClient(timeout=10.0) as client:
        batch = random.sample(REQUESTS, k=min(6, len(REQUESTS)))
        for method, url in batch:
            await hit_endpoint(client, method, url)
            await asyncio.sleep(0.2)


async def main() -> None:
    print(f"Failure simulator started (interval={INTERVAL}s)")
    while True:
        await run_cycle()
        await asyncio.sleep(INTERVAL)


if __name__ == "__main__":
    asyncio.run(main())
