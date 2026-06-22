from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
import uuid


class RoleRead(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    priority_level: str

    class Config:
        from_attributes = True


class PermissionRead(BaseModel):
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    resource: str
    action: str

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    email: str
    username: str
    full_name: str
    password: str
    phone: Optional[str] = None
    designation: Optional[str] = None
    badge_number: Optional[str] = None
    department: Optional[str] = None
    jurisdiction: Optional[str] = None
    preferred_language: Optional[str] = "en"


class UserLogin(BaseModel):
    username: str
    password: str


class UserRead(BaseModel):
    id: uuid.UUID
    email: str
    username: str
    full_name: str
    phone: Optional[str] = None
    designation: Optional[str] = None
    badge_number: Optional[str] = None
    department: Optional[str] = None
    jurisdiction: Optional[str] = None
    is_active: bool
    is_superuser: bool
    last_login: Optional[datetime] = None
    preferred_language: str
    roles: List[RoleRead] = []
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    designation: Optional[str] = None
    department: Optional[str] = None
    jurisdiction: Optional[str] = None
    preferred_language: Optional[str] = None


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserRead


class TokenRefresh(BaseModel):
    refresh_token: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str = Field(..., min_length=8)
