import jwt
import json
import urllib.request
import os

# Supabase project URL and JWKS endpoint
SUPABASE_URL = os.environ.get("SUPABASE_URL")
if not SUPABASE_URL:
    raise ValueError("SUPABASE_URL environment variable not set.")
JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"

# The JWT retrieved from the previous step
with open("supabase_tests/jwt.token", "r") as f:
    JWT_TOKEN = f.read().strip()

def get_jwks():
    """Fetches the JWKS from the Supabase endpoint."""
    with urllib.request.urlopen(JWKS_URL) as response:
        if response.status != 200:
            raise Exception(f"Failed to fetch JWKS: HTTP {response.status}")
        return json.loads(response.read().decode('utf-8'))

def get_public_key(kid, jwks, alg):
    """Finds the public key in the JWKS that matches the given Key ID (kid) and algorithm."""
    for jwk in jwks.get("keys", []):
        if jwk.get("kid") == kid and jwk.get("alg") == alg:
            if alg == "RS256":
                return jwt.algorithms.RSAAlgorithm.from_jwk(jwk)
            elif alg == "ES256":
                return jwt.algorithms.ECAlgorithm.from_jwk(jwk)
    raise ValueError(f"Public key not found in JWKS for kid {kid} and alg {alg}")

def test_verify_jwt():
    """Verifies the JWT using the public key from the JWKS endpoint."""
    # Get the header from the token to find the Key ID (kid) and algorithm (alg)
    unverified_header = jwt.get_unverified_header(JWT_TOKEN)
    kid = unverified_header.get("kid")
    alg = unverified_header.get("alg")
    print(f"Token Header: kid={kid}, alg={alg}")

    # Fetch the JWKS and find the public key
    jwks = get_jwks()
    print("JWKS content:", json.dumps(jwks, indent=2))
    jwks_kids = [jwk.get("kid") for jwk in jwks.get("keys", [])]
    print(f"JWKS Kids: {jwks_kids}")

    # If the algorithm is HS256, it's a legacy token, and we can't verify it with JWKS
    if alg == "HS256":
        print("This token is signed with HS256. It cannot be verified with JWKS.")
        print("Please ensure your Supabase project is configured to sign JWTs with RS256 or ES256.")
        return

    try:
        public_key = get_public_key(kid, jwks, alg)

        # Decode and verify the token
        decoded_token = jwt.decode(
            JWT_TOKEN,
            public_key,
            algorithms=[alg],
            audience="authenticated",
            issuer=f"{SUPABASE_URL}/auth/v1",
        )
        print("Token successfully verified!")
        print("Decoded token:", decoded_token)
        assert decoded_token["email"] == "test@test.com"
    except jwt.PyJWTError as e:
        print(f"Token verification failed: {e}")
        assert False, f"Token verification failed: {e}"

if __name__ == "__main__":
    test_verify_jwt()