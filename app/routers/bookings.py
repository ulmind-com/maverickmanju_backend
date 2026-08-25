from fastapi import APIRouter, Depends, Query

from .. import crud, db
from ..schemas import BookingIn, BookingPatch
from ..security import current_admin

public = APIRouter(prefix="/api/bookings", tags=["bookings"])
admin = APIRouter(
    prefix="/api/admin/bookings", tags=["bookings-admin"], dependencies=[Depends(current_admin)]
)


@public.post("", status_code=201)
async def create_booking(payload: BookingIn):
    """Public booking form submission. Returns the reference number to show the guest."""
    sequence = await db.next_sequence("booking")
    doc = {
        **payload.model_dump(),
        "referenceNumber": f"MM-{sequence:04d}",
        "status": "new",
        "internalNote": "",
        "createdAt": db.now(),
        "updatedAt": db.now(),
    }
    result = await db.bookings().insert_one(doc)
    return db.serialize(await db.bookings().find_one({"_id": result.inserted_id}))


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
