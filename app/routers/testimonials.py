from fastapi import APIRouter, Depends

from .. import crud, db, storage
from ..schemas import TestimonialIn, TestimonialPatch
from ..security import current_admin

public = APIRouter(prefix="/api/testimonials", tags=["testimonials"])
admin = APIRouter(
    prefix="/api/admin/testimonials",
    tags=["testimonials-admin"],
    dependencies=[Depends(current_admin)],
)


@public.get("")
async def list_published():
    return await crud.list_docs(db.testimonials(), only_published=True)


@admin.get("")
async def list_all():
    return await crud.list_docs(db.testimonials())


@admin.post("", status_code=201)
async def create(payload: TestimonialIn):
    return await crud.create_doc(db.testimonials(), payload.model_dump())


@admin.patch("/{item_id}")
async def update(item_id: str, payload: TestimonialPatch):
    return await crud.update_doc(
        db.testimonials(), item_id, payload.model_dump(exclude_unset=True)
    )


@admin.delete("/{item_id}", status_code=204)
async def delete(item_id: str):
    doc = await crud.delete_doc(db.testimonials(), item_id)
    await storage.delete_asset(doc.get("publicId", ""), "video")
    await storage.delete_asset(doc.get("photoPublicId", ""), "image")
