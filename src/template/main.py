from fastapi import FastAPI, Depends
from fastapi_supabase import (
    SupabaseAuthConfig,
    JWTAuthenticator,
    add_cors_middleware
)

app = FastAPI()

# Initialize configuration
config = SupabaseAuthConfig.from_env()

# Initialize the JWT authenticator
jwt_auth = JWTAuthenticator(config)

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