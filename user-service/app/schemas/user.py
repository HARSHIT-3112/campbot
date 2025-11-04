from pydantic import BaseModel, EmailStr
from typing import Optional

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
    role: Optional[str] = "student"
    org_id: Optional[int]

class UserOut(BaseModel):
    id: int
    email: EmailStr
    username: Optional[str]
    role: str
    org_id: Optional[int]

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
