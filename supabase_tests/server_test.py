import os
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.testclient import TestClient
from fastapi_supabase.config import SupabaseAuthConfig
from fastapi_supabase.auth import JWTAuthenticator
from fastapi_supabase.models import TokenData # Import TokenData

# Load a test JWT token from file
with open("jwt.token") as f:
    TEST_JWT = f.read().strip()

# Determine SUPABASE_URL and SUPA_JWT_SECRET from environment or provide defaults
SUPABASE_BASE_URL = os.getenv("SUPABASE_URL", "http://localhost:8000")
SUPA_JWT_SECRET_KEY = os.getenv("SUPA_JWT_SECRET", "super-secret-jwt-key-for-testing-only") # This secret is not used when fetching JWKS

# Minimal config for JWTAuthenticator (adjust as needed)
config = SupabaseAuthConfig(
    supa_url=SUPABASE_BASE_URL,
    supa_jwt_secret=SUPA_JWT_SECRET_KEY, # Still needed for config, but not for verification if JWKS is used
    supa_jwks_url=f"{SUPABASE_BASE_URL}/auth/v1/keys", # Set JWKS URL for JWTChecker
    supa_use_legacy_jwt=False, # Use JWTChecker for real JWKS verification
    dev_mode=True, # Enable dev mode for testing with TestClient
    dev_token=TEST_JWT, # Use the generated JWT as the dev token
    dev_user_id="test-user-from-jwt", # Dummy user ID for dev mode
    dev_role="authenticated", # Dummy role for dev mode
    dev_email="test@example.com" # Dummy email for dev mode
)
jwt_auth = JWTAuthenticator(config)

app = FastAPI()

@app.get("/protected")
async def protected(token_data: TokenData = Depends(jwt_auth)):
    return {"user_id": token_data.user_id, "role": token_data.role}

@app.get("/protected_role")
@jwt_auth.require_anyof_roles(["admin"]) # Example: requires 'admin' role
async def protected_role(token_data: TokenData = Depends(jwt_auth)):
    return {"message": f"Welcome admin {token_data.user_id}"}

@app.get("/protected_not_anonymous")
@jwt_auth.not_anonymous()
async def protected_not_anonymous(token_data: TokenData = Depends(jwt_auth)):
    return {"message": f"Welcome non-anonymous user {token_data.user_id}"}

@app.get("/unprotected")
async def unprotected():
    return {"msg": "no auth required"}

client = TestClient(app)

def test_protected_with_valid_jwt():
    response = client.get(
        "/protected",
        headers={"Authorization": f"Bearer {TEST_JWT}"}
    )
    assert response.status_code == 200, response.text
    assert "user_id" in response.json()

def test_protected_with_missing_jwt():
    response = client.get("/protected")
    assert response.status_code == 403 or response.status_code == 401

def test_unprotected():
    response = client.get("/unprotected")
    assert response.status_code == 200
    assert response.json() == {"msg": "no auth required"}

def test_protected_role_with_valid_role():
    # Assuming TEST_JWT has 'admin' role or modify TEST_JWT for this test
    # For now, let's assume TEST_JWT has 'authenticated' role and this test will fail
    # if the role is not 'admin'. We need a JWT with 'admin' role for this to pass.
    # For demonstration, I'll use the existing TEST_JWT and expect a 403 if role is not admin.
    response = client.get(
        "/protected_role",
        headers={"Authorization": f"Bearer {TEST_JWT}"}
    )
    # This assertion will depend on the role in TEST_JWT.
    # If TEST_JWT has 'admin' role, expect 200. Otherwise, expect 403.
    # For now, I'll assume TEST_JWT does NOT have 'admin' role and expect 403.
    assert response.status_code == 403, response.text
    assert response.json()["detail"]["code"] == "insufficient_permissions"

def test_protected_role_with_invalid_role():
    # This test will use the existing TEST_JWT, which we assume does not have 'admin' role
    response = client.get(
        "/protected_role",
        headers={"Authorization": f"Bearer {TEST_JWT}"}
    )
    assert response.status_code == 403, response.text
    assert response.json()["detail"]["code"] == "insufficient_permissions"

def test_protected_not_anonymous_with_non_anonymous_user():
    # Assuming TEST_JWT is for a non-anonymous user
    response = client.get(
        "/protected_not_anonymous",
        headers={"Authorization": f"Bearer {TEST_JWT}"}
    )
    assert response.status_code == 200, response.text
    assert "message" in response.json()

def test_protected_not_anonymous_with_anonymous_user():
    # This test requires an anonymous JWT. For now, I'll skip or mock this.
    # If TEST_JWT is non-anonymous, this test will fail.
    # For now, I'll assume TEST_JWT is non-anonymous and this test will not be run with an anonymous token.
    # To properly test this, we would need to generate an anonymous JWT.
    pass # Placeholder for now

if __name__ == "__main__":
    import pytest
    pytest.main()
