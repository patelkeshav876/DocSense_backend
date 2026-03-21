from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class DocumentBase(BaseModel):
    filename: str
    file_type: str
    file_size: int

class DocumentCreate(DocumentBase):
    pass

class Document(DocumentBase):
    id: str
    content: Optional[str]
    user_id: str
    uploaded_at: datetime
    processed_at: Optional[datetime]

    class Config:
        from_attributes = True

class ChatMessageBase(BaseModel):
    role: str
    content: str

class ChatMessageCreate(ChatMessageBase):
    document_id: str

class ChatMessage(ChatMessageBase):
    id: str
    document_id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True

class AskRequest(BaseModel):
    question: str