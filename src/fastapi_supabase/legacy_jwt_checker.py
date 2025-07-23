from functools import wraps
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Dict, List, Optional, Callable
from datetime import datetime
from .config import SupabaseAuthConfig
from .models import TokenData

class LegacyJWTChecker:
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

    async def decode_token(self, token: str) -> Dict:
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
            payload = await self.decode_token(credentials.credentials)
            
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