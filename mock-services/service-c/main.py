import os
import random
import sys

from fastapi import FastAPI, HTTPException

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.fci_middleware import register_fci_handlers

SERVICE_NAME = "service-c"
app = FastAPI(title=SERVICE_NAME)
register_fci_handlers(app, SERVICE_NAME)


def maybe_fail(rate: float = 0.3):
    if random.random() < rate:
        errors = [
            HTTPException(status_code=500, detail="Downstream API returned 503 Service Unavailable"),
            HTTPException(status_code=500, detail="Circuit breaker open for external payment API"),
            HTTPException(status_code=500, detail="DNS resolution failed for api.external.com"),
        ]
        raise random.choice(errors)


@app.get("/health")
def health():
    return {"status": "ok", "service": SERVICE_NAME}


@app.get("/api/payments/{payment_id}")
def get_payment(payment_id: str):
    maybe_fail()
    return {"id": payment_id, "status": "completed"}


@app.post("/api/payments/charge")
def charge_payment(payment: dict):
    maybe_fail(0.4)
    return {"charged": True, **payment}


@app.get("/api/notifications")
def get_notifications():
    maybe_fail()
    return {"notifications": []}


@app.get("/api/external/status")
def external_status():
    maybe_fail(0.35)
    return {"external": "ok"}
