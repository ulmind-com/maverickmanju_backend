from fastapi import APIRouter, Depends
from pymongo import ReturnDocument

from .. import db
from ..schemas import SiteSettingsIn
from ..security import current_admin

public = APIRouter(prefix="/api/settings", tags=["settings"])
admin = APIRouter(
    prefix="/api/admin/settings", tags=["settings-admin"], dependencies=[Depends(current_admin)]
)


def _clean(doc: dict | None) -> dict:
    if doc is None:
        return {}
    out = {k: v for k, v in doc.items() if k not in {"_id", "updatedAt"}}
    return out


@public.get("")
async def get_settings():
    return _clean(await db.site_settings().find_one({"_id": "site"}))


@admin.put("")
async def update_settings(payload: SiteSettingsIn):
    doc = await db.site_settings().find_one_and_update(
        {"_id": "site"},
        {"$set": {**payload.model_dump(), "updatedAt": db.now()}},
        upsert=True,
        return_document=ReturnDocument.AFTER,
    )
    return _clean(doc)
