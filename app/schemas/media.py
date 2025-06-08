from pydantic import BaseModel

class UploadImage(BaseModel):
    id: int
    target_model: bool = False # False: Site, True: List
