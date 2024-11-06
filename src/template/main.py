import logging
from fastapi import FastAPI, Depends
from fastapi_supabase import (
    SupabaseAuthConfig,
    JWTAuthenticator,
    add_cors_middleware
)

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
        config: SupabaseAuthConfig =  SupabaseAuthConfig()
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
async def protected_endpoint(token_data = Depends(jwt_auth)):
    return {
        "message": "This is a protected endpoint",
        "user_id": token_data.user_id,
        "role": token_data.role,
        "expires_at": token_data.exp.isoformat(),
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}