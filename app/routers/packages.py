from fastapi import APIRouter, Depends

from .. import crud, db, storage
from ..schemas import PackageIn, PackagePatch
from ..security import current_admin

public = APIRouter(prefix="/api/packages", tags=["packages"])
admin = APIRouter(
    prefix="/api/admin/packages", tags=["packages-admin"], dependencies=[Depends(current_admin)]
)


@public.get("")
async def list_published():
    """Event packages rendered under 'Formats by occasion' on /services."""
    return await crud.list_docs(db.packages(), only_published=True)


@admin.get("")
async def list_all():
    return await crud.list_docs(db.packages())


@admin.post("", status_code=201)
async def create(payload: PackageIn):
    return await crud.create_doc(db.packages(), payload.model_dump())


@admin.patch("/{item_id}")
async def update(item_id: str, payload: PackagePatch):
    return await crud.update_doc(db.packages(), item_id, payload.model_dump(exclude_unset=True))


@admin.delete("/{item_id}", status_code=204)
async def delete(item_id: str):
    doc = await crud.delete_doc(db.packages(), item_id)
    await storage.delete_asset(doc.get("publicId", ""), "image")
