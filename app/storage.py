"""Cloudinary media uploads."""

import io
from typing import Any

import cloudinary
import cloudinary.uploader
from fastapi import HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool

from .config import settings

cloudinary.config(
    cloud_name=settings.cloudinary_cloud_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True,
)

# Cloudinary switches to chunked uploads above this size.
_CHUNK_THRESHOLD = 20 * 1024 * 1024
_CHUNK_SIZE = 6 * 1024 * 1024


def _resource_type(content_type: str | None) -> str:
    if content_type and content_type.startswith("video/"):
        return "video"
    if content_type and content_type.startswith("image/"):
        return "image"
    return "auto"


def _video_poster(url: str) -> str:
    """Cloudinary renders any video frame as an image by swapping the extension."""
    base, _, ext = url.rpartition(".")
    return f"{base}.jpg" if base and ext else url


def _do_upload(
    data: bytes, resource_type: str, folder: str, filename: str
) -> dict[str, Any]:
    stream = io.BytesIO(data)
    # Cloudinary reads `.name` off the stream to honour use_filename.
    stream.name = filename or "upload"
    options: dict[str, Any] = {
        "resource_type": resource_type,
        "folder": folder,
        "use_filename": True,
        "unique_filename": True,
        "overwrite": False,
    }
    if len(data) > _CHUNK_THRESHOLD:
        return cloudinary.uploader.upload_large(stream, chunk_size=_CHUNK_SIZE, **options)
    return cloudinary.uploader.upload(stream, **options)


async def upload_file(file: UploadFile, subfolder: str = "") -> dict[str, Any]:
    """Upload one image or video and return the fields the admin UI stores."""
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file.")

    limit = settings.max_upload_mb * 1024 * 1024
    if len(data) > limit:
        raise HTTPException(
            status_code=413,
            detail=f"File is larger than the {settings.max_upload_mb}MB upload limit.",
        )

    folder = f"{settings.cloudinary_folder}/{subfolder}".rstrip("/")
    try:
        result = await run_in_threadpool(
            _do_upload, data, _resource_type(file.content_type), folder, file.filename or ""
        )
    except Exception as exc:  # cloudinary raises a broad Error type
        raise HTTPException(status_code=502, detail=f"Upload failed: {exc}")

    url = result.get("secure_url") or result.get("url") or ""
    resource_type = result.get("resource_type", "image")
    return {
        "url": url,
        "publicId": result.get("public_id", ""),
        "resourceType": resource_type,
        "type": "video" if resource_type == "video" else "image",
        "thumbnailUrl": _video_poster(url) if resource_type == "video" else url,
        "bytes": result.get("bytes", len(data)),
        "format": result.get("format", ""),
    }


async def delete_asset(public_id: str, resource_type: str = "image") -> None:
    """Best-effort cleanup — a failed delete must never block a record delete."""
    if not public_id:
        return
    try:
        await run_in_threadpool(
            cloudinary.uploader.destroy, public_id, resource_type=resource_type, invalidate=True
        )
    except Exception:
        pass
