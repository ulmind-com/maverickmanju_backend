from fastapi import APIRouter, Depends

from .. import crud, db, storage
from ..schemas import GalleryIn, GalleryPatch
from ..security import current_admin

public = APIRouter(prefix="/api/gallery", tags=["gallery"])
admin = APIRouter(
    prefix="/api/admin/gallery", tags=["gallery-admin"], dependencies=[Depends(current_admin)]
)


@public.get("")
async def list_published():
    """Every published image and video, in admin display order."""
    return await crud.list_docs(db.gallery(), only_published=True)


@admin.get("")
async def list_all():
    return await crud.list_docs(db.gallery())


@admin.post("", status_code=201)
async def create(payload: GalleryIn):
    return await crud.create_doc(db.gallery(), payload.model_dump())


@admin.patch("/{item_id}")
async def update(item_id: str, payload: GalleryPatch):
    return await crud.update_doc(db.gallery(), item_id, payload.model_dump(exclude_unset=True))


@admin.delete("/{item_id}", status_code=204)
async def delete(item_id: str):
    doc = await crud.delete_doc(db.gallery(), item_id)
    await storage.delete_asset(doc.get("publicId", ""), doc.get("type", "image"))
    await storage.delete_asset(doc.get("thumbnailPublicId", ""), "image")
