import os
import logging
from typing import Any, List, Optional

# from pydantic import BaseConfig
from pydantic_settings import BaseSettings
from typing import Optional, List
# from dotenv import load_dotenv as _load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

class SupabaseAuthConfig(BaseSettings):

    supa_jwt_secret: Optional[str] = None
    supa_url: Optional[str] = None
    supa_anon_key: Optional[str] = None
    supa_use_legacy_jwt: bool = False
    supa_jwks_url: Optional[str] = None


    origins: Optional[List[str]] = None
    dev_mode: bool = False
    dev_token: Optional[str] = None
    dev_user_id: Optional[str] = "dev-user"
    dev_role: Optional[str] = "authenticated"
    dev_email: Optional[str] = "dev@email.com"

 
    class Config:
        env_file = ".env"  # This loads environment variables from a .env file
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "allow"          # This allows extra fields in the environment

    from pydantic import field_validator

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.dev_mode:
            # This warning is now handled by the validator for dev_mode
            # logger.info(f"Dev mode enabled with token: {self.dev_token}")
            logger.info(f"Dev user: {self.dev_user_id} with role: {self.dev_role}")

    @field_validator("origins", mode="before")
    @classmethod
    def parse_origins(cls, value: Any) -> Optional[List[str]]:
        if isinstance(value, str):
            return [x.strip() for x in value.split(",")]
        if isinstance(value, list):
            return value
        return None # Or raise error, or return default

    @field_validator("dev_mode", mode="before")
    @classmethod
    def parse_dev_mode(cls, value: Any) -> bool:
        if isinstance(value, str):
            val = value.lower() == 'true'
            if val:
                logger.warning('Running in DEV MODE, do not use in production')
            return val
        if isinstance(value, bool):
            if value:
                logger.warning('Running in DEV MODE, do not use in production')
            return value
        return False # Default to False if not a string or bool
