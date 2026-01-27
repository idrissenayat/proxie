"""
Media schemas for Proxie.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime


class MediaAttachment(BaseModel):
    """A media attachment in a chat message."""
    type: Literal["image", "video"] = Field(..., description="Type of media")
    data: str = Field(..., description="Base64-encoded media data")
    mime_type: str = Field(..., description="MIME type (e.g., image/jpeg, video/mp4)")
    filename: Optional[str] = Field(None, description="Original filename")


class StoredMedia(BaseModel):
    """A media file stored on the server."""
    id: str = Field(..., description="Unique media ID")
    url: str = Field(..., description="URL to access the media")
    type: Literal["image", "video"] = Field(..., description="Type of media")
    mime_type: str = Field(..., description="MIME type")
    filename: Optional[str] = None
    size_bytes: int = Field(..., description="File size in bytes")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    session_id: Optional[str] = Field(None, description="Associated chat session")


class MediaUploadResponse(BaseModel):
    """Response after uploading media."""
    success: bool
    media: Optional[StoredMedia] = None
    error: Optional[str] = None


class MediaValidationError(BaseModel):
    """Media validation error details."""
    field: str
    message: str
