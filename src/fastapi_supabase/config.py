import os
import logging
from typing import Optional, List
from dotenv import load_dotenv as _load_dotenv

# Configure logging
logger = logging.getLogger(__name__)

class SupabaseAuthConfig:
    """Configuration class for Supabase Authentication
    
    Handles JWT authentication configuration and CORS origins for FastAPI applications
    using Supabase authentication.
    """
    def __init__(
        self,
        jwt_secret: str,
        origins: Optional[List[str]] = None,
        algorithm: str = "HS256"
    ):
        if not jwt_secret:
            raise ValueError("JWT_SECRET is required")
            
        logger.debug("Initializing SupabaseAuthConfig")
        self.jwt_secret = jwt_secret
        self.origins = origins or []
        self.algorithm = algorithm

    @classmethod
    def from_env(cls, load_dotenv: bool = True) -> 'SupabaseAuthConfig':
        """
        Creates configuration from environment variables.
        
        Args:
            load_dotenv (bool): Whether to load .env file. Defaults to True.
            
        Returns:
            SupabaseAuthConfig: Configuration instance
            
        Raises:
            ValueError: If required environment variables are missing
        """
        logger.debug("Loading configuration from environment")
        
        if load_dotenv:
            logger.debug("Loading .env file")
            _load_dotenv()

        jwt_secret = os.getenv("JWT_SECRET")
        if not jwt_secret:
            raise ValueError("JWT_SECRET environment variable is required")

        origins = os.getenv("ORIGINS", "").split(",") if os.getenv("ORIGINS") else []
        
        config = cls(
            jwt_secret=jwt_secret,
            origins=origins,
        )
        
        logger.debug("Configuration loaded successfully")
        return config