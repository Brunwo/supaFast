from fastapi import FastAPI, Depends
from auth import  TokenData, JWTAuthenticator
from middleware import add_cors_middleware  # Import the CORS setup
import config
# import auth

app = FastAPI()
# Initialize the JWT bearer with your secret
jwt_auth = JWTAuthenticator(config.JWT_SECRET)

add_cors_middleware(app)

@app.get("/public")
async def public_endpoint():
    return {"message": "This is a public endpoint"}


@app.get("/protected")
async def protected_endpoint(token_data: TokenData = Depends(jwt_auth)):
    # token_data contains the decoded JWT information (e.g., user_id)
    return {"message": "This is a protected endpoint", 
        "user_id": token_data.user_id,
        "role": token_data.role,
        "expires_at": token_data.exp.isoformat(),
        }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}