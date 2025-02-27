import os
from pathlib import Path

from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
#from firebase_admin.auth import verify_id_token
from pydantic_settings import BaseSettings

bearer_scheme = HTTPBearer(auto_error=False)


class Settings(BaseSettings):
    """Database and application settings read from environment variables"""
    
    company_name: str
    company_reg: str
    company_address: str
    company_nif: str
    database_hostname: str
    database_port: str
    database_password: str
    database_name: str
    database_username: str
    secret_key: str
    refresh_secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    email: str
    email_password: str
    smtp_server: str
    smtp_port: int
    domain: str
    email_auth_code_expire_minutes: int
    email_recovery_code_expire_minutes: int
    google_application_credentials: str
    nominatim_base_url: str
    user_agent: str

    class Config:
        env_file = os.path.join(Path(__file__).resolve().parent.parent, ".env")
        env_file_encoding = "utf-8"

settings = Settings()