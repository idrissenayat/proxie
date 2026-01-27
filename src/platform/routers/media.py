"""
Media router for Proxie.

Handles media upload and serving endpoints.
"""

from fastapi import APIRouter, HTTPException, Request, UploadFile, File
from fastapi.responses import FileResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from typing import List
import base64

from src.platform.services.media import media_service, UPLOAD_DIR
from src.platform.schemas.media import MediaAttachment, MediaUploadResponse, StoredMedia
from src.platform.config import settings

router = APIRouter(
    prefix="/media",
    tags=["media"],
)

limiter = Limiter(key_func=get_remote_address)


@router.post("/upload", response_model=MediaUploadResponse)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def upload_media(
    request: Request,
    attachment: MediaAttachment,
    session_id: str = None
):
    """
    Upload a single media file (base64 encoded).
    """
    # Validate
    is_valid, error = media_service.validate_attachment(attachment)
    if not is_valid:
        return MediaUploadResponse(success=False, error=error)
    
    try:
        # Store
        stored = media_service.store_attachment(attachment, session_id)
        return MediaUploadResponse(success=True, media=stored)
    except Exception as e:
        return MediaUploadResponse(success=False, error=str(e))


@router.post("/upload-file", response_model=MediaUploadResponse)
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def upload_media_file(
    request: Request,
    file: UploadFile = File(...),
    session_id: str = None
):
    """
    Upload a media file directly (multipart form).
    """
    # Read file
    content = await file.read()
    
    # Determine type
    if file.content_type.startswith("image/"):
        media_type = "image"
    elif file.content_type.startswith("video/"):
        media_type = "video"
    else:
        return MediaUploadResponse(
            success=False, 
            error=f"Unsupported content type: {file.content_type}"
        )
    
    # Create attachment
    attachment = MediaAttachment(
        type=media_type,
        data=base64.b64encode(content).decode("utf-8"),
        mime_type=file.content_type,
        filename=file.filename
    )
    
    # Validate
    is_valid, error = media_service.validate_attachment(attachment)
    if not is_valid:
        return MediaUploadResponse(success=False, error=error)
    
    try:
        # Store
        stored = media_service.store_attachment(attachment, session_id)
        return MediaUploadResponse(success=True, media=stored)
    except Exception as e:
        return MediaUploadResponse(success=False, error=str(e))


@router.get("/{filename}")
async def get_media(filename: str):
    """
    Retrieve a media file by filename.
    """
    filepath = media_service.get_media_path(filename)
    if not filepath:
        raise HTTPException(status_code=404, detail="Media not found")
    
    return FileResponse(filepath)


@router.delete("/{media_id}")
@limiter.limit(f"{settings.RATE_LIMIT_PER_MINUTE}/minute")
async def delete_media(request: Request, media_id: str):
    """
    Delete a media file.
    """
    deleted = media_service.delete_media(media_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Media not found")
    
    return {"success": True, "message": f"Media {media_id} deleted"}
