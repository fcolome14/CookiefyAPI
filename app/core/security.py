from passlib.context import CryptContext
from jose import jwt, JWTError
from app.core.config import settings
from app.utils.date_time import TimeUtils
import bcrypt

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    """ Hashes a password using bcrypt with an automatically generated salt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hashed version."""
    #return pwd_context.verify(plain_password, hashed_password)
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

# JWT Token Management
def create_access_token(data: dict) -> str:
    """Create a JWT access token with expiration."""
    to_encode = data.copy()
    expire = TimeUtils().exp_time()
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)

def decode_access_token(token: str) -> dict | None:
    """Decode and validate a JWT access token."""
    try:
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None
