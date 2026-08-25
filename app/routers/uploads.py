from fastapi import APIRouter, Depends, File, Form, UploadFile

from .. import storage
from ..security import current_admin

router = APIRouter(
    prefix="/api/admin/uploads", tags=["uploads"], dependencies=[Depends(current_admin)]
)


@router.post("", status_code=201)
async def upload(file: UploadFile = File(...), folder: str = Form(default="")):
    """Upload one image or video to Cloudinary and return its public URL."""
    return await storage.upload_file(file, subfolder=folder)
