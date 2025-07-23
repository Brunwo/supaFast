import uvicorn
import logging
from fastapi import FastAPI, Depends
from dotenv import load_dotenv
import os

# Determine the path to the .env file relative to this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(BASE_DIR, '.env')

# Load the .env file before importing SupabaseAuthConfig
if os.path.exists(ENV_PATH):
    load_dotenv(ENV_PATH)
    logging.info(f"Loaded environment variables from: {ENV_PATH}")
else:
    logging.warning(f".env file not found at: {ENV_PATH}. Relying on environment variables.")


# from fastapi_supabase.config import SupabaseAuthConfig
from fastapi_supabase import (JWTAuthenticator, add_cors_middleware)
from fastapi_supabase.config import SupabaseAuthConfig
from fastapi_supabase.models import TokenData

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI()

def initialize_auth():
    """
    Initialize authentication configuration and JWT authenticator
    
    Returns:
        tuple: (SupabaseAuthConfig, JWTAuthenticator)
    """
    try:
        config: SupabaseAuthConfig =  SupabaseAuthConfig(
            supa_url=os.getenv("SUPABASE_URL"),
            supa_anon_key=os.getenv("SUPABASE_ANON_KEY"),
            supa_jwks_url=f"{os.getenv("SUPABASE_URL")}/auth/v1/.well-known/jwks.json",
            supa_use_legacy_jwt=os.getenv("SUPABASE_USE_LEGACY_JWT", "False").lower() == "true"
        )
        jwt_auth = JWTAuthenticator(config)
        return config, jwt_auth
    except Exception as e:
        logger.error(f"Failed to initialize authentication: {e}")
        raise

# Initialize authentication
config, jwt_auth = initialize_auth()

# Add CORS middleware
add_cors_middleware(app, config)

@app.get("/public")
async def public_endpoint():
    return {"message": "This is a public endpoint"}

@app.get("/protected")
@jwt_auth.require_anyof_roles(["authenticated"])
async def protected_endpoint(token_data: TokenData = Depends(jwt_auth)):
    return {
        "message": "This is a protected endpoint",
        "user_id": token_data.user_id,
        "role": token_data.role,
        "expires_at": token_data.exp.isoformat(),
        "is_anonymous": token_data.is_anonymous,
    }

@app.get("/not_anonymous")
@jwt_auth.not_anonymous()
async def protected_endpoint(token_data: TokenData = Depends(jwt_auth)):
    return {
        "message": "This is a protected endpoint",
        "user_id": token_data.user_id,
        "role": token_data.role,
        "expires_at": token_data.exp.isoformat(),
        "is_anonymous": token_data.is_anonymous,
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)