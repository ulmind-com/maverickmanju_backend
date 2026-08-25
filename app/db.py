"""Mongo connection, collection handles and document helpers."""

from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import HTTPException
from pymongo import AsyncMongoClient, ReturnDocument

from .config import settings

_client: AsyncMongoClient | None = None


def client() -> AsyncMongoClient:
    global _client
    if _client is None:
        _client = AsyncMongoClient(settings.mongodb_uri, tz_aware=True)
    return _client


def db():
    return client()[settings.mongodb_db]


# --- collection handles -------------------------------------------------
def gallery():
    return db()["gallery_items"]


def testimonials():
    return db()["testimonials"]


def service_images():
    return db()["service_images"]


def packages():
    return db()["event_packages"]


def bookings():
    return db()["bookings"]


def site_settings():
    return db()["site_settings"]


def admin_users():
    return db()["admin_users"]


def counters():
    return db()["counters"]


# --- helpers ------------------------------------------------------------
def now() -> datetime:
    return datetime.now(timezone.utc)


def oid(value: str) -> ObjectId:
    """Parse a path id, returning 404 rather than 500 for malformed ids."""
    try:
        return ObjectId(value)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="Not found")


def serialize(doc: dict[str, Any] | None) -> dict[str, Any] | None:
    """Mongo document -> JSON-friendly dict with `id` instead of `_id`."""
    if doc is None:
        return None
    out = dict(doc)
    out["id"] = str(out.pop("_id"))
    for key, value in out.items():
        if isinstance(value, datetime):
            out[key] = value.isoformat()
        elif isinstance(value, ObjectId):
            out[key] = str(value)
    return out


async def next_sequence(name: str) -> int:
    """Atomic auto-increment used for booking reference numbers."""
    doc = await counters().find_one_and_update(
        {"_id": name},
        {"$inc": {"value": 1}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return int(doc["value"])


async def create_indexes() -> None:
    await admin_users().create_index("email", unique=True)
    await service_images().create_index("slug", unique=True)
    await gallery().create_index([("sortOrder", 1), ("createdAt", -1)])
    await testimonials().create_index([("sortOrder", 1), ("createdAt", -1)])
    await packages().create_index([("sortOrder", 1), ("createdAt", -1)])
    await bookings().create_index([("createdAt", -1)])
    await bookings().create_index("referenceNumber", unique=True)


async def close() -> None:
    global _client
    if _client is not None:
        await _client.close()
        _client = None
