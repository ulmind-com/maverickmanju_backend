import secrets

from fastapi import APIRouter, Depends, HTTPException, Query
from pymongo.errors import DuplicateKeyError

from .. import crud, db
from ..schemas import BookingIn, BookingPatch
from ..security import current_admin
from .availability import is_blocked

public = APIRouter(prefix="/api/bookings", tags=["bookings"])
admin = APIRouter(
    prefix="/api/admin/bookings", tags=["bookings-admin"], dependencies=[Depends(current_admin)]
)


# No I/O/0/1 — these get misread when a reference is repeated over the phone.
_REF_ALPHABET = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"


def _reference() -> str:
    """MM-<yy>-<4 random chars>, e.g. MM-26-K7F3.

    Deliberately not a running count: a sequential reference tells every client
    exactly how many bookings have ever been taken.
    """
    year = db.now().strftime("%y")
    suffix = "".join(secrets.choice(_REF_ALPHABET) for _ in range(4))
    return f"MM-{year}-{suffix}"


@public.post("", status_code=201)
async def create_booking(payload: BookingIn):
    """Public booking form submission. Returns the reference number to show the guest."""
    # Enforced here as well as in the UI — the form can be bypassed, this cannot.
    if await is_blocked(payload.date):
        raise HTTPException(
            status_code=409,
            detail="That date is already booked. Please pick another date.",
        )

    doc = {
        **payload.model_dump(),
        "status": "new",
        "internalNote": "",
        "createdAt": db.now(),
        "updatedAt": db.now(),
    }

    # referenceNumber carries a unique index, so retry on the rare collision.
    for _ in range(8):
        try:
            result = await db.bookings().insert_one({**doc, "referenceNumber": _reference()})
        except DuplicateKeyError:
            continue
        return db.serialize(await db.bookings().find_one({"_id": result.inserted_id}))

    raise HTTPException(status_code=500, detail="Could not allocate a reference number.")


@admin.get("")
async def list_bookings(
    status: str | None = Query(default=None),
    search: str | None = Query(default=None),
):
    query: dict = {}
    if status and status != "all":
        query["status"] = status
    if search:
        query["$or"] = [
            {field: {"$regex": search, "$options": "i"}}
            for field in ("name", "mobile", "email", "location", "referenceNumber", "venue")
        ]
    cursor = db.bookings().find(query).sort([("createdAt", -1)])
    return [db.serialize(doc) async for doc in cursor]


@admin.patch("/{booking_id}")
async def update_booking(booking_id: str, payload: BookingPatch):
    return await crud.update_doc(
        db.bookings(), booking_id, payload.model_dump(exclude_unset=True)
    )


@admin.delete("/{booking_id}", status_code=204)
async def delete_booking(booking_id: str):
    await crud.delete_doc(db.bookings(), booking_id)
