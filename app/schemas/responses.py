from pydantic import BaseModel, EmailStr
from typing import Any, List, Optional, Tuple, Union
from typing import Union

class MetaData(BaseModel):

    request_id: Optional[str] = None
    client: Optional[str] = None

class SuccessResponse(BaseModel):
    """Common success request response body"""

    status: str = "success"
    message: Union[str, dict, None] = None
    data: Union[str, dict, None] = None
    meta: Optional[MetaData] = None

class ErrorResponse(BaseModel):
    """Common error request response body"""

    status: str = "error"
    message: Union[str, dict, None] = None
    detail: Union[str, dict, None] = None
    meta: Optional[MetaData] = None
