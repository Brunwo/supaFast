from functools import wraps
from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from typing import Dict, List, Optional, Callable
from datetime import datetime
from .config import SupabaseAuthConfig
import httpx
from cachetools import TTLCache
from .models import TokenData

class JWTChecker:
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
        self.jwks_cache = TTLCache(maxsize=1, ttl=3600)  # Cache JWKS for 1 hour

    async def get_jwks(self):
        if "jwks" in self.jwks_cache:
            return self.jwks_cache["jwks"]

        async with httpx.AsyncClient() as client:
            try:
                res = await client.get(self.config.supa_jwks_url)
                res.raise_for_status()
                jwks = res.json()
                self.jwks_cache["jwks"] = jwks
                return jwks
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail={"code": "jwks_fetch_failed", "message": f"Failed to fetch JWKS: {e}"}
                )

    def get_public_key(self, kid: str, jwks: Dict, alg: str):
        for jwk in jwks.get("keys", []):
            if jwk.get("kid") == kid and jwk.get("alg") == alg:
                if alg == "RS256":
                    return jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
                elif alg == "ES256":
                    return jwt.algorithms.ECAlgorithm.from_jwk(jwk)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "invalid_kid", "message": "Invalid Key ID or Algorithm"}
        )

    async def decode_token(self, token: str) -> Dict:
        if self.config.dev_mode and self.config.dev_token:
            if token == self.config.dev_token:
                return {
                    "sub": self.config.dev_user_id,
                    "role": self.config.dev_role,
                    "email": self.config.dev_email,
                    "exp": datetime.now().timestamp() + 3600,
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
            unverified_header = jwt.get_unverified_header(token)
            kid = unverified_header.get("kid")
            alg = unverified_header.get("alg")
            if not kid or not alg:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={"code": "missing_kid_or_alg", "message": "Missing Key ID or Algorithm in token header"}
                )

            jwks = await self.get_jwks()
            public_key = self.get_public_key(kid, jwks, alg)

            return jwt.decode(
                token,
                public_key,
                algorithms=[alg],
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
        try:
            payload = await self.decode_token(credentials.credentials)
            
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
            payload = await self.decode_token(credentials.credentials)
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