from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    username: str
    password: str

class UserRead(BaseModel):
    id: int
    full_name: str
    name: str
    email: EmailStr

    class Config:
        from_attributes = True
