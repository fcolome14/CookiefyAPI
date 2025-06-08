from pydantic import BaseModel

class UploadImage(BaseModel):
    id: int
    is_media: bool = False # False: Site, True: List
