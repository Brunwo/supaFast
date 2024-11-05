from typing import Optional, List

class SupabaseAuthConfig:
    """Configuration class for Supabase Authentication"""
    def __init__(
        self,
        jwt_secret: str,
        origins: Optional[List[str]] = None,
        algorithm: str = "HS256"
    ):
        self.jwt_secret = jwt_secret
        self.origins = origins or []
        self.algorithm = algorithm

    @classmethod
    def from_env(cls, load_dotenv=True):
        """
        Optional factory method to create config from environment variables
        Only use this if you explicitly want to support .env files
        """
        from dotenv import load_dotenv as _load_dotenv
        import os
        
        if load_dotenv:
            _load_dotenv()
            
        return cls(
            jwt_secret=os.getenv("JWT_SECRET", ""),
            origins=os.getenv("ORIGINS", "").split(",") if os.getenv("ORIGINS") else [],
        )