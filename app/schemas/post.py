from pydantic import BaseModel, ConfigDict, field_serializer, Field
from typing import List as TypingList, Optional
from app.core.config import settings
from app.models.image import Image
from datetime import datetime

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
    image: Optional[int] = None
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
    image: Optional[Image] # type: ignore

    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    @field_serializer("image")
    def serialize_image(self, image_file: Optional[Image]) -> Optional[str]: # type: ignore
        if image_file:
            print("DEBUG → path:", image_file.path)
            return f"{settings.image_domain}/{image_file.path}"
        return None

class ImageRead(BaseModel):
    id: int
    path: str
    model_config = ConfigDict(from_attributes=True)

class ListKPIs(BaseModel):
    id: int
    likes: int
    shares: int
    saves: int
    visit_count: int
    image: int
    created_at: datetime

class SiteKPIs(BaseModel):
    click_count: int
    lists_count: int

class Score(BaseModel):
    score: float

class ListBasicRead(BaseModel):
    id: int
    name: str
    image_file: Optional[ImageRead]

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("image_file")
    def serialize_image(self, image_file: Optional[ImageRead]) -> Optional[str]:
        if image_file:
            return f"{settings.image_domain}/{image_file.path}"
        return None

class SiteBasicRead(BaseModel):
    id: int
    name: str
    image: Optional[ImageRead]

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("image")
    def serialize_image(self, image_file: Optional[ImageRead]) -> Optional[str]:
        if image_file:
            return f"{settings.image_domain}/{image_file.path}"
        return None

class HashtagBasicRead(BaseModel):
    id: int
    name: str
    image_file: Optional[ImageRead] = Field(alias="image")  # maps Hashtag.image → image_file

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("image_file")
    def serialize_image(self, image_file: Optional[ImageRead]) -> Optional[str]:
        if image_file:
            return f"{settings.image_domain}/{image_file.path}"
        return None

class HashtagWithCount(BaseModel):
    count: int
    hashtag: HashtagBasicRead

class ListRead(BaseModel):
    id: int
    name: str
    description: Optional[str]
    likes: int
    shares: int
    saves: int
    image_file: Optional[ImageRead]
    accepts_contributions: bool
    is_public: bool
    sites: TypingList[SiteRead]

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("image_file")
    def serialize_image(self, image_file: Optional[ImageRead]) -> Optional[str]:
        if image_file:
            print("DEBUG → path:", image_file.path)
            return f"{settings.image_domain}/{image_file.path}"
        return None

class ListDelete(BaseModel):
    id: list[int]

class PostRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
