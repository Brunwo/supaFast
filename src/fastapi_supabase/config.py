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
    origins: Optional[List[str]] 
    # algorithm: str = "HS256"

    class Config:
        env_file = ".env"  # This loads environment variables from a .env file
        extra = "allow"          # This allows extra fields in the environment

    @classmethod
    def parse_env_var(cls, field_name: str, raw_val: str) -> Any:
        if field_name == 'origins':
            return [x.strip() for x in raw_val.split(',')]
        return cls.json_loads(raw_val)
