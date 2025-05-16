from pydantic import BaseModel

class ListCreate(BaseModel):
    name: str
    description: str
    accepts_contributions: bool
    is_public: bool

class ListUpdate(BaseModel):
    id: int
    name: str
    description: str
    likes: int
    shares: int
    saves: int
    image: str
    sites: list[int]
    accepts_contributions: bool
    is_public: bool

class PostRead(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
