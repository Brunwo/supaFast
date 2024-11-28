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

    supa_jwt_secret: str
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

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.dev_mode:
            logger.info(f"Dev mode enabled with token: {self.dev_token}")
            logger.info(f"Dev user: {self.dev_user_id} with role: {self.dev_role}")

    @classmethod
    def parse_env_var(cls, field_name: str, raw_val: str) -> Any:
        if field_name == 'origins':
            return [x.strip() for x in raw_val.split(',')]

        if field_name == 'dev_mode' and raw_val.lower() == 'true':
                logger.warning('Running in DEV MODE, do not use in production')
                logger.debug(f'Loading dev mode from env var: {raw_val}')
                return True

        return cls.json_loads(raw_val)
