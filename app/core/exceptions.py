# app/core/exceptions.py

from fastapi import Request, status
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from app.schemas.responses import ErrorResponse
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

async def rate_limit_handler(_: Request, exc: RateLimitExceeded):
    """Handle rate limit exceeded exceptions."""
    message = exc.detail.split(" ")
    if len(message) >= 4:
        every, unit = message[2], message[3]
        retry_after = f"{every} {unit}"
    else:
        retry_after = "a short period"

    # Create the error response
    error_response = ErrorResponse(
        message="Max. attempts reached",
        data=f"You have exceeded the allowed number of requests. Please try again after {retry_after}.",
    )

    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content=error_response.model_dump(),
    )
