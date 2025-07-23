from functools import wraps
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Dict, List, Optional, Callable
from datetime import datetime
from .config import SupabaseAuthConfig
from .jwt_checker import JWTChecker
from .legacy_jwt_checker import LegacyJWTChecker
from .models import TokenData

class JWTAuthenticator:
    def __init__(
        self, 
        config: SupabaseAuthConfig,
        aud: Optional[str] = None,
        iss: Optional[str] = None,
        leeway: int = 30,
    ):
        self.config = config
        if config.supa_use_legacy_jwt:
            self.checker = LegacyJWTChecker(config, aud, iss, leeway)
        else:
            self.checker = JWTChecker(config, aud, iss, leeway)

    async def __call__(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ) -> TokenData:
        return await self.checker(credentials)
        
    def require_auth(self , func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, credentials: HTTPAuthorizationCredentials = Security(HTTPBearer()), **kwargs):
            payload = await self.checker.decode_token(credentials.credentials)
            token_data = TokenData(
                user_id=payload["sub"],
                role=payload.get("role"),
                email=payload.get("email"),
                exp=datetime.fromtimestamp(payload["exp"]),
                aud=payload.get("aud"),
                iss=payload.get("iss"),
                is_anonymous=payload.get("is_anonymous", True)
            )
            return await func(*args, token_data=token_data, **kwargs)
        return wrapper

    def require_anyof_roles(self, required_roles: List[str]) -> Callable:
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, token_data: TokenData = Depends(self), **kwargs):
                if not any(role  == token_data.role for role in required_roles):
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail={
                            "code": "insufficient_permissions",
                            "message": f"Required roles: {required_roles}, current roles: {token_data.role}"
                        }
                    )
                return await func(*args, token_data=token_data, **kwargs)
            return wrapper
        return decorator
    
    def not_anonymous(self) -> Callable:
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, token_data: TokenData = Depends(self), **kwargs):
                if token_data.is_anonymous:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail={
                            "code": "anonymous_access_denied",
                            "message": f"Anonymous users are not allowed to access this endpoint"
                        }
                        )
                return await func(*args, token_data=token_data, **kwargs)
            return wrapper
        return decorator
