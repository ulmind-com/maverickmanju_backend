"""The four core performance sections on /services — only the image is editable."""

from fastapi import APIRouter, Depends, HTTPException
from pymongo import ReturnDocument

from .. import db, storage
from ..schemas import SERVICE_SLUGS, ServiceImagePatch
from ..security import current_admin

public = APIRouter(prefix="/api/service-images", tags=["service-images"])
admin = APIRouter(
    prefix="/api/admin/service-images",
    tags=["service-images-admin"],
    dependencies=[Depends(current_admin)],
)


async def _all() -> list[dict]:
    cursor = db.service_images().find({}).sort([("sortOrder", 1)])
    return [db.serialize(doc) async for doc in cursor]


@public.get("")
async def list_images():
    return await _all()


@admin.get("")
async def list_images_admin():
    return await _all()


@admin.put("/{slug}")
async def set_image(slug: str, payload: ServiceImagePatch):
    if slug not in SERVICE_SLUGS:
        raise HTTPException(status_code=404, detail="Unknown service section.")

    previous = await db.service_images().find_one({"slug": slug})
    doc = await db.service_images().find_one_and_update(
        {"slug": slug},
        {
            "$set": {
                "imageUrl": payload.imageUrl,
                "publicId": payload.publicId,
                "updatedAt": db.now(),
            }
        },
        return_document=ReturnDocument.AFTER,
    )
    if doc is None:
        raise HTTPException(status_code=404, detail="Unknown service section.")

    # Drop the replaced Cloudinary asset so the media library does not grow forever.
    old_public_id = (previous or {}).get("publicId", "")
    if old_public_id and old_public_id != payload.publicId:
        await storage.delete_asset(old_public_id, "image")
    return doc
