from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import jwt
from typing import Optional, Dict
from datetime import datetime
from .config import SupabaseAuthConfig

class TokenData(BaseModel):
    user_id: str
    role: Optional[str] = None
    email: Optional[str] = None
    exp: datetime
    aud: Optional[str] = None
    iss: Optional[str] = None

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
        """Decode and verify the JWT token"""
        try:
            decoded_secret = self.config.supa_jwt_secret.encode('utf-8')
            
            # Configure verification options
            options = {
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": bool(self.aud),  # Only verify if aud is provided
                "verify_iss": bool(self.iss),  # Only verify if iss is provided
                "leeway": self.leeway,  # Allow some time skew
            }

            payload = jwt.decode(
                token,
                decoded_secret,
                algorithms=["HS256"],
                audience=self.aud,
                issuer=self.iss,
                options=options
            )
            
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "token_expired",
                    "message": "Token has expired"
                }
            )
        except jwt.InvalidAudienceError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "invalid_audience",
                    "message": "Token has invalid audience"
                }
            )
        except jwt.InvalidIssuerError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "invalid_issuer",
                    "message": "Token has invalid issuer"
                }
            )
        except jwt.InvalidTokenError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "invalid_token",
                    "message": f"Invalid token: {str(e)}"
                }
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
                iss=payload.get("iss")
            )

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "code": "authentication_failed",
                    "message": f"Authentication failed: {str(e)}"
                }
            )
