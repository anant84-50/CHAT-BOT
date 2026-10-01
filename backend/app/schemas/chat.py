from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class MessageBase(BaseModel):
    role: str
    content: str
    input_type: str = "text"
    output_type: str = "text"
    sources: Optional[List[dict]] = None


class MessageCreate(MessageBase):
    conversation_id: int

class Message(MessageBase):
    id: int
    conversation_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class ConversationBase(BaseModel):
    title: str

class ConversationCreate(ConversationBase):
    pass

class Conversation(ConversationBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    messages: List[Message] = []

    class Config:
        from_attributes = True

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[int] = None
    file_id: Optional[int] = None # For image/doc references if needed

class ChatResponse(BaseModel):
    reply: str
    conversation_id: int
    sources: Optional[List[dict]] = None
