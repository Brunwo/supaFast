from functools import wraps
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
from typing import Dict, List, Optional, Callable
from datetime import datetime
from .config import SupabaseAuthConfig

class TokenData(BaseModel):
    user_id: str
    role: str
    email: Optional[str] = None
    exp: datetime
    aud: Optional[str] = None
    iss: Optional[str] = None
    is_anonymous : bool = True

class JWTAuthenticator:
    def __init__(
        self, 
        config: SupabaseAuthConfig,
        aud: Optional[str] = None,
        iss: Optional[str] = None,
        leeway: int = 30,
    ):
        self.config = config
        self.aud = aud
        self.iss = iss
        self.leeway = leeway
        self.security = HTTPBearer()

    def decode_token(self, token: str) -> Dict:
        # Check for dev mode first
        if self.config.dev_mode and self.config.dev_token:
            if token == self.config.dev_token:
                return {
                    "sub": self.config.dev_user_id,
                    "role": self.config.dev_role,
                    "email": self.config.dev_email,
                    "exp": datetime.now().timestamp() + 3600,  # 1 hour from now
                    "aud": self.aud,
                    "iss": self.iss,
                    "is_anonymous": False
                }
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={"code": "invalid_dev_token", "message": "Invalid development token"}
                )

        try:
            decoded_secret = self.config.supa_jwt_secret.encode('utf-8')
            return jwt.decode(
                token,
                decoded_secret,
                algorithms=["HS256"],
                audience=self.aud,
                issuer=self.iss,
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "verify_aud": bool(self.aud),
                    "verify_iss": bool(self.iss),
                    "leeway": self.leeway,
                }
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "token_expired", "message": "Token has expired"}
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"code": "invalid_token", "message": str(e)}
            )

    async def __call__(
        self, 
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ) -> TokenData:
        """FastAPI dependency for token verification"""
        try:
            payload = self.decode_token(credentials.credentials)
            
            # Extract required claims
            user_id = payload.get("sub")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "code": "missing_sub_claim",
                        "message": "Token missing required sub claim"
                    }
                )

            return TokenData(
                user_id=user_id,
                role=payload.get("role"),
                email=payload.get("email"),
                exp=datetime.fromtimestamp(payload["exp"]),
                aud=payload.get("aud"),
                iss=payload.get("iss"),
                is_anonymous=payload.get("is_anonymous", True)
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "authentication_failed",
                    "message": f"Authentication failed: {str(e)}"
                }
            )
        
    def require_auth(self , func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, credentials: HTTPAuthorizationCredentials = Security(HTTPBearer()), **kwargs):
            payload = self.decode_token(credentials.credentials)
            token_data = TokenData(
                user_id=payload["sub"],
                role=payload.get("role"),
                email=payload.get("email"),
                exp=datetime.fromtimestamp(payload["exp"]),
                aud=payload.get("aud"),
                iss=payload.get("iss"),
                # type=payload.get("type", "authenticated")
            )
            print('here')
            return await func(*args, token_data=token_data, **kwargs)
        return wrapper

    def require_anyof_roles(self, required_roles: List[str]) -> Callable:
        """
        Decorator that checks if the authenticated user has any of the required roles
        Args:
            required_roles: List of roles that are allowed to access the endpoint
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, token_data: TokenData = Depends(self), **kwargs):
                # Check if user has any of the required roles
                if not any(role  == token_data.role for role in required_roles):
                # if any(.role in token_data.role):
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
        """
        Decorator that checks if the authenticated user is not anonymous : as this is possible if supabase anonymous login is enabled
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            async def wrapper(*args, token_data: TokenData = Depends(self), **kwargs):
                # Check if user has any of the required roles
                if token_data.is_anonymous:
                # if any(.role in token_data.role):
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
