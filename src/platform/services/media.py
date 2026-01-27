"""
Media storage service for Proxie.

Handles upload, storage, and retrieval of media files (images/videos).
"""

import os
import base64
import uuid
import logging
import mimetypes
from typing import Optional, Tuple, List
from datetime import datetime, timedelta
from pathlib import Path

from src.platform.schemas.media import MediaAttachment, StoredMedia
from src.platform.config import settings

logger = logging.getLogger(__name__)

# Media storage configuration
UPLOAD_DIR = Path("uploads")
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
MAX_VIDEO_SIZE = 10 * 1024 * 1024  # 10MB
MAX_MEDIA_COUNT = 5
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}
ALLOWED_VIDEO_TYPES = {"video/mp4", "video/webm", "video/quicktime"}
MEDIA_EXPIRY_HOURS = 24


class MediaService:
    """Service for handling media uploads and storage."""
    
    def __init__(self):
        # Ensure upload directory exists
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        logger.info(f"Media upload directory: {UPLOAD_DIR.absolute()}")
    
    def validate_attachment(self, attachment: MediaAttachment) -> Tuple[bool, Optional[str]]:
        """
        Validate a media attachment.
        Returns (is_valid, error_message).
        """
        # Check type
        if attachment.type == "image":
            if attachment.mime_type not in ALLOWED_IMAGE_TYPES:
                return False, f"Invalid image type: {attachment.mime_type}. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}"
        elif attachment.type == "video":
            if attachment.mime_type not in ALLOWED_VIDEO_TYPES:
                return False, f"Invalid video type: {attachment.mime_type}. Allowed: {', '.join(ALLOWED_VIDEO_TYPES)}"
        else:
            return False, f"Invalid media type: {attachment.type}"
        
        # Decode and check size
        try:
            data = base64.b64decode(attachment.data)
            size = len(data)
            
            if attachment.type == "image" and size > MAX_IMAGE_SIZE:
                return False, f"Image too large: {size / 1024 / 1024:.1f}MB. Maximum: {MAX_IMAGE_SIZE / 1024 / 1024}MB"
            if attachment.type == "video" and size > MAX_VIDEO_SIZE:
                return False, f"Video too large: {size / 1024 / 1024:.1f}MB. Maximum: {MAX_VIDEO_SIZE / 1024 / 1024}MB"
                
        except Exception as e:
            return False, f"Invalid base64 data: {str(e)}"
        
        return True, None
    
    def validate_attachments(self, attachments: List[MediaAttachment]) -> Tuple[bool, Optional[str]]:
        """
        Validate a list of attachments.
        """
        if len(attachments) > MAX_MEDIA_COUNT:
            return False, f"Too many attachments: {len(attachments)}. Maximum: {MAX_MEDIA_COUNT}"
        
        for i, attachment in enumerate(attachments):
            is_valid, error = self.validate_attachment(attachment)
            if not is_valid:
                return False, f"Attachment {i + 1}: {error}"
        
        return True, None
    
    def store_attachment(self, attachment: MediaAttachment, session_id: Optional[str] = None) -> StoredMedia:
        """
        Store a media attachment and return the stored media info.
        """
        # Generate unique ID
        media_id = str(uuid.uuid4())
        
        # Determine file extension
        ext = mimetypes.guess_extension(attachment.mime_type) or ""
        if ext == ".jpe":
            ext = ".jpg"
        
        # Create filename
        filename = f"{media_id}{ext}"
        filepath = UPLOAD_DIR / filename
        
        # Decode and save
        data = base64.b64decode(attachment.data)
        with open(filepath, "wb") as f:
            f.write(data)
        
        # Generate URL (relative path for now, can be updated for CDN)
        url = f"/media/{filename}"
        
        stored = StoredMedia(
            id=media_id,
            url=url,
            type=attachment.type,
            mime_type=attachment.mime_type,
            filename=attachment.filename,
            size_bytes=len(data),
            created_at=datetime.utcnow(),
            session_id=session_id
        )
        
        logger.info(f"Stored media: {media_id} ({attachment.type}, {len(data)} bytes)")
        return stored
    
    def store_attachments(
        self, 
        attachments: List[MediaAttachment], 
        session_id: Optional[str] = None
    ) -> List[StoredMedia]:
        """
        Store multiple attachments.
        """
        return [self.store_attachment(att, session_id) for att in attachments]
    
    def get_media_path(self, filename: str) -> Optional[Path]:
        """
        Get the file path for a media file.
        """
        filepath = UPLOAD_DIR / filename
        if filepath.exists():
            return filepath
        return None
    
    def delete_media(self, media_id: str) -> bool:
        """
        Delete a media file by its ID.
        """
        for filepath in UPLOAD_DIR.iterdir():
            if filepath.stem == media_id:
                filepath.unlink()
                logger.info(f"Deleted media: {media_id}")
                return True
        return False
    
    def cleanup_expired_media(self, hours: int = MEDIA_EXPIRY_HOURS) -> int:
        """
        Delete media files older than the specified hours.
        Returns the number of files deleted.
        """
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        deleted = 0
        
        for filepath in UPLOAD_DIR.iterdir():
            if filepath.is_file():
                mtime = datetime.fromtimestamp(filepath.stat().st_mtime)
                if mtime < cutoff:
                    filepath.unlink()
                    deleted += 1
                    logger.info(f"Cleaned up expired media: {filepath.name}")
        
        return deleted
    
    def prepare_for_gemini(self, stored_media: StoredMedia) -> dict:
        """
        Prepare stored media for sending to Gemini API.
        Returns a dict with mime_type and data for inline_data.
        """
        filepath = self.get_media_path(stored_media.url.split("/")[-1])
        if not filepath:
            raise FileNotFoundError(f"Media not found: {stored_media.id}")
        
        with open(filepath, "rb") as f:
            data = base64.b64encode(f.read()).decode("utf-8")
        
        return {
            "mime_type": stored_media.mime_type,
            "data": data
        }


# Global service instance
media_service = MediaService()
