"""
Chat schemas for Proxie.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from uuid import UUID

from src.platform.schemas.media import MediaAttachment, StoredMedia


class DraftRequest(BaseModel):
    """A draft service request awaiting user approval."""
    service_type: str = Field(..., description="Type of service")
    service_category: str = Field(..., description="Service category")
    description: str = Field(..., description="Detailed description")
    details: Dict[str, Any] = Field(default_factory=dict, description="Additional details")
    location: Dict[str, str] = Field(..., description="Location info (city, etc.)")
    budget: Dict[str, float] = Field(..., description="Budget range (min, max)")
    timing: Optional[str] = Field(None, description="Timing preference")
    media: List[StoredMedia] = Field(default_factory=list, description="Attached media")
    specialist_notes: Optional[str] = Field(None, description="Internal notes from specialist")


class ChatRequest(BaseModel):
    """Request to send a message to the chat agent."""
    message: Optional[str] = Field(None, description="User's text message")
    session_id: Optional[str] = Field(None, description="Session ID for continuity")
    role: str = Field("consumer", description="User role: consumer or provider")
    consumer_id: Optional[UUID] = Field(None, description="Consumer ID if role is consumer")
    provider_id: Optional[UUID] = Field(None, description="Provider ID if role is provider")
    enrollment_id: Optional[UUID] = Field(None, description="Enrollment ID if role is enrollment")
    media: Optional[List[MediaAttachment]] = Field(None, description="Media attachments")
    action: Optional[Literal["approve_request", "edit_request", "cancel_request", "submit_enrollment", "submit_offer"]] = Field(
        None, description="Workflow action for specialized requests"
    )


class ChatResponse(BaseModel):
    """Response from the chat agent."""
    session_id: str = Field(..., description="Session ID for follow-up messages")
    message: str = Field(..., description="Agent's text response")
    data: Optional[Dict[str, Any]] = Field(None, description="Structured data (offers, bookings, etc.)")
    draft: Optional[DraftRequest] = Field(None, description="Draft request awaiting approval")
    awaiting_approval: bool = Field(False, description="Whether agent is waiting for user to approve/edit/cancel")
