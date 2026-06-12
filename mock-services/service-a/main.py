import os
import random
import sys

from fastapi import FastAPI, HTTPException

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from shared.fci_middleware import register_fci_handlers

SERVICE_NAME = "service-a"
app = FastAPI(title=SERVICE_NAME)
register_fci_handlers(app, SERVICE_NAME)


def maybe_fail(rate: float = 0.3):
    if random.random() < rate:
        errors = [
            HTTPException(status_code=500, detail="JWT token expired"),
            HTTPException(status_code=500, detail="Invalid auth configuration: missing JWT_SECRET"),
            HTTPException(status_code=500, detail="Environment variable API_KEY not set"),
        ]
        raise random.choice(errors)


@app.get("/health")
def health():
    return {"status": "ok", "service": SERVICE_NAME}


@app.get("/api/users/{user_id}")
def get_user(user_id: str):
    maybe_fail()
    return {"id": user_id, "name": f"User {user_id}"}


@app.post("/api/users/login")
def login(credentials: dict):
    maybe_fail(0.4)
    if not credentials.get("token"):
        raise HTTPException(status_code=500, detail="Authentication failed: token required")
    return {"access_token": "mock-token"}


@app.get("/api/config")
def get_config():
    maybe_fail(0.35)
    return {"feature_flags": {"beta": True}}


@app.get("/api/profile")
def get_profile():
    maybe_fail()
    return {"profile": "active"}
