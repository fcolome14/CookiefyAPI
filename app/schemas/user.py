from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    username: str
    password: str

class VerifyCodeRequest(BaseModel):
    email: EmailStr
    code: int
    
class NewPasswordRequest(BaseModel):
    email: EmailStr

class PasswordReset(BaseModel):
    email: EmailStr
    new_password: str

class UserRead(BaseModel):
    id: int
    full_name: str
    name: str
    email: EmailStr

    class Config:
        from_attributes = True
