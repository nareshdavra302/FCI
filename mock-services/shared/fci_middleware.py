import asyncio
import os
import traceback
from datetime import datetime, timezone

import httpx
from fastapi import HTTPException, Request
from starlette.responses import JSONResponse


FCI_INGEST_URL = os.getenv("FCI_INGEST_URL", "http://localhost:8000/api/v1/failures")
SERVICE_NAME = os.getenv("SERVICE_NAME", "unknown-service")


async def _send_failure(payload: dict) -> None:
    delays = [0.5, 1.0, 2.0]
    for attempt, delay in enumerate(delays, start=1):
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.post(FCI_INGEST_URL, json=payload)
                if response.status_code < 500:
                    return
        except Exception:
            if attempt == len(delays):
                return
        await asyncio.sleep(delay)


async def _report_failure(request: Request, name: str, status_code: int, error_message: str, stack: str | None = None):
    payload = {
        "service_name": name,
        "endpoint": str(request.url.path),
        "method": request.method,
        "status_code": status_code,
        "error_message": error_message,
        "stack_trace": stack,
        "request_metadata": {
            "query_params": dict(request.query_params),
            "client_host": request.client.host if request.client else None,
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    asyncio.create_task(_send_failure(payload))


def register_fci_handlers(app, service_name: str | None = None):
    name = service_name or SERVICE_NAME

    @app.exception_handler(HTTPException)
    async def fci_http_exception_handler(request: Request, exc: HTTPException):
        if exc.status_code >= 500:
            await _report_failure(request, name, exc.status_code, str(exc.detail))
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail, "service": name})

    @app.exception_handler(Exception)
    async def fci_exception_handler(request: Request, exc: Exception):
        stack = traceback.format_exc()
        await _report_failure(request, name, 500, str(exc), stack)
        return JSONResponse(status_code=500, content={"detail": str(exc), "service": name})
