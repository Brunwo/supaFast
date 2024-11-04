from fastapi import FastAPI, Depends
from auth import verify_token, TokenData

app = FastAPI()

@app.get("/public")
async def public_endpoint():
    return {"message": "This is a public endpoint"}

@app.get("/protected")
async def protected_endpoint(token_data: TokenData = Depends(verify_token)):
    # token_data contains the decoded JWT information (e.g., user_id)
    return {"message": "This is a protected endpoint", "user_id": token_data.user_id}
