
import os
import functions_framework
from flask import request, jsonify
from fastapi_supabase.auth import JWTAuthenticator
from fastapi_supabase.config import SupabaseAuthConfig

# Initialize authentication
# The secret will be loaded from an environment variable
try:
    config = SupabaseAuthConfig.from_env()
    auth = JWTAuthenticator(config)
except Exception as e:
    # Handle cases where env vars might not be set on initial load
    print(f"Could not initialize authenticator: {e}")
    auth = None

@functions_framework.http
def protected_endpoint(req):
    """
    An HTTP-triggered Cloud Function that requires Supabase JWT authentication.
    """
    if not auth:
        return jsonify({"error": "Authenticator not initialized. Check JWT_SECRET environment variable."}), 500

    # Get the token from the Authorization header
    auth_header = req.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return jsonify({"error": "Missing or invalid Authorization header"}), 401

    token = auth_header.split("Bearer ")[1]

    try:
        # Decode and validate the token
        token_data = auth.decode_token(token)

        # Check for required role (optional, customize as needed)
        required_role = "authenticated"
        if token_data.get("role") != required_role:
            return jsonify({
                "error": "Insufficient permissions",
                "message": f"Required role: '{required_role}', your role: '{token_data.get('role')}'"
            }), 403

        # If valid, return the user data
        return jsonify({
            "message": "Access granted",
            "user_id": token_data.get("sub"),
            "role": token_data.get("role"),
            "email": token_data.get("email")
        }), 200

    except Exception as e:
        return jsonify({"error": "Invalid token", "details": str(e)}), 401
