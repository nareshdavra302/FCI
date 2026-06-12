import os
import random
import sys

from fastapi import FastAPI, HTTPException

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.fci_middleware import register_fci_handlers

SERVICE_NAME = "service-b"
app = FastAPI(title=SERVICE_NAME)
register_fci_handlers(app, SERVICE_NAME)


def maybe_fail(rate: float = 0.3):
    if random.random() < rate:
        errors = [
            HTTPException(status_code=500, detail="Database connection refused: postgres://db:5432"),
            HTTPException(status_code=500, detail="Query timeout after 30000ms"),
            HTTPException(status_code=500, detail="Connection pool exhausted: max connections reached"),
        ]
        raise random.choice(errors)


@app.get("/health")
def health():
    return {"status": "ok", "service": SERVICE_NAME}


@app.get("/api/orders/{order_id}")
def get_order(order_id: str):
    maybe_fail()
    return {"id": order_id, "status": "pending"}


@app.post("/api/orders")
def create_order(order: dict):
    maybe_fail(0.35)
    return {"id": "ord-123", **order}


@app.get("/api/inventory")
def get_inventory():
    maybe_fail()
    return {"items": 42}


@app.get("/api/reports")
def get_reports():
    maybe_fail(0.4)
    return {"reports": []}
