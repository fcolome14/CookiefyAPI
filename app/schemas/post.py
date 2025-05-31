from pydantic import BaseModel, ConfigDict, field_serializer
from typing import List as TypingList, Optional
from app.core.config import settings

class ListCreate(BaseModel):
    name: str
    description: str
    accepts_contributions: bool
    is_public: bool

class ListUpdate(BaseModel):
    id: int
    name: Optional[str] = None
    description: Optional[str] = None
    likes: Optional[int] = None
    shares: Optional[int] = None
    saves: Optional[int] = None
    image: Optional[str] = None
    sites: Optional[list[int]] = None
    accepts_contributions: Optional[bool] = None
    is_public: Optional[bool] = None

class HashtagRead(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class SiteRead(BaseModel):
    id: int
    name: str
    address: Optional[str]
    city: Optional[str]
    contact: Optional[str]
    hashtags: TypingList[HashtagRead]  # nested

    model_config = ConfigDict(from_attributes=True)

class ListRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    likes: int
    shares: int
    saves: int
    image: int
    accepts_contributions: bool
    is_public: bool
    sites: TypingList[SiteRead]  # nested

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("image")
    def serialize_image(self, image_id: int) -> str:
        return f"{settings.image_domain}/posts/get-image/{image_id}"

class ListDelete(BaseModel):
    id: list[int]

class PostRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
