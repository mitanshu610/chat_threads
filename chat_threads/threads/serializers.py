from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, Any, Dict


class CreateThreadRequest(BaseModel):
    title: str
    product: Optional[str]
    requested_by: Optional[str]
    user_id: Optional[int] = None
    meta: Optional[dict]
    alternate_id: Optional[int] = None
    org_id: Optional[str] = None



class CreateMessageRequest(BaseModel):
    role: str
    content: str
    product: str
    display_text: Optional[str] = None
    is_json: bool = False
    thread_id: Optional[UUID] = None
    parent_message_id: Optional[int] = None
    requested_by: Optional[str] = None
    question_config: Optional[dict] = None
    prompt_details: Optional[dict] = None

class ThreadSchema(BaseModel):
    id: int
    uuid: UUID
    title: str
    product: str
    user_email: str
    user_id: Optional[int] = None
    alternate_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    last_message_id: Optional[int] = None
    is_deleted: bool
    meta: Optional[Dict[str, Any]] = None
    org_id: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class ThreadMessageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    thread_uuid: UUID
    parent_message_id: Optional[int] = None
    content: Optional[str] = None
    role: str
    display_text: Optional[str] = None
    is_json: bool = False
    is_disliked: Optional[bool] = None
    is_deleted: bool = False
    user_id: Optional[int] = None
    question_config: Optional[dict] = None
    prompt_details: Optional[dict] = None