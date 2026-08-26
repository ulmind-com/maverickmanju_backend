"""Dates the artist is already booked on.

The public site reads these to grey out days in the booking calendar; the
booking endpoint refuses an enquiry that lands on one of them, so a client
cannot get through by editing the form.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from pymongo.errors import DuplicateKeyError

from .. import db
from ..schemas import BlockedDateIn, BlockedDatesIn
from ..security import current_admin

public = APIRouter(prefix="/api/availability", tags=["availability"])
admin = APIRouter(
    prefix="/api/admin/availability",
    tags=["availability-admin"],
    dependencies=[Depends(current_admin)],
)


async def is_blocked(date: str) -> bool:
    if not date:
        return False
    return await db.blocked_dates().find_one({"date": date}) is not None


async def block_for_booking(date: str, note: str) -> None:
    """Blocks a date on behalf of a confirmed booking.

    Upserts with $setOnInsert so a date the admin had already blocked keeps its
    own note. Freeing a date stays a manual decision — a cancelled booking does
    not silently reopen the day.
    """
    if not date:
        return
    await db.blocked_dates().update_one(
        {"date": date},
        {"$setOnInsert": {"date": date, "note": note, "createdAt": db.now()}},
        upsert=True,
    )


@public.get("")
async def list_blocked(
    start: str | None = Query(default=None, description="YYYY-MM-DD, inclusive"),
    end: str | None = Query(default=None, description="YYYY-MM-DD, inclusive"),
):
    """Blocked dates only — internal notes are never exposed publicly."""
    query: dict = {}
    if start or end:
        bounds: dict = {}
        if start:
            bounds["$gte"] = start
        if end:
            bounds["$lte"] = end
        query["date"] = bounds

    cursor = db.blocked_dates().find(query, {"date": 1, "_id": 0}).sort("date", 1)
    return {"dates": [doc["date"] async for doc in cursor]}


@admin.get("")
async def list_blocked_admin():
    cursor = db.blocked_dates().find({}).sort("date", 1)
    return [db.serialize(doc) async for doc in cursor]


@admin.post("", status_code=201)
async def block_date(payload: BlockedDateIn):
    try:
        await db.blocked_dates().insert_one(
            {"date": payload.date, "note": payload.note, "createdAt": db.now()}
        )
    except DuplicateKeyError:
        raise HTTPException(status_code=409, detail="That date is already blocked.")
    return db.serialize(await db.blocked_dates().find_one({"date": payload.date}))


@admin.put("")
async def replace_dates(payload: BlockedDatesIn):
    """Blocks every date in the list in one call, skipping any already blocked."""
    existing = {doc["date"] async for doc in db.blocked_dates().find({}, {"date": 1})}
    fresh = [d for d in dict.fromkeys(payload.dates) if d not in existing]
    if fresh:
        await db.blocked_dates().insert_many(
            [{"date": d, "note": payload.note, "createdAt": db.now()} for d in fresh]
        )
    return {"added": fresh}


@admin.delete("/{date}", status_code=204)
async def unblock_date(date: str):
    result = await db.blocked_dates().delete_one({"date": date})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="That date was not blocked.")
