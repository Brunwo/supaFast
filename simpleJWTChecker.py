import base64
import hmac
import hashlib
from typing import Tuple, Dict
import json
import config


def base64url_decode(input: str) -> bytes:
    """Decode base64url-encoded string"""
    # Add padding if needed
    padding = 4 - (len(input) % 4)
    if padding != 4:
        input += '=' * padding
    return base64.urlsafe_b64decode(input)

def verify_jwt(token: str, secret: str) -> Tuple[bool, Dict]:
    """
    Verify JWT token using HMAC-SHA256, similar to jwt.io's approach
    
    Args:
        token: The JWT token string
        secret: The secret key used for signing
        
    Returns:
        Tuple of (is_valid, decoded_payload)
    """
    try:
        # Split the token into parts
        header_b64, payload_b64, signature_b64 = token.split('.')
        
        # Create the message that was signed
        message = f"{header_b64}.{payload_b64}"
    
        # Calculate the signature
        key = secret.encode('utf-8')
        message_bytes = message.encode('utf-8')
        expected_signature = base64.urlsafe_b64encode(
            hmac.new(key, message_bytes, hashlib.sha256).digest()
        ).rstrip(b'=').decode('utf-8')
        
        # Compare signatures
        is_valid = hmac.compare_digest(expected_signature, signature_b64)
        
        # Decode payload if signature is valid
        if is_valid:
            payload = json.loads(base64url_decode(payload_b64))
            return True, payload
        else:
            return False, {}
            
    except Exception as e:
        print(f"Error verifying token: {str(e)}")
        return False, {}

# Example usage
if __name__ == "__main__":
    # Your JWT token and secret
    jwt_token = config.TEST_TOKEN
    jwt_secret = config.JWT_SECRET
    
    # Verify the token
    is_valid, payload = verify_jwt(jwt_token, jwt_secret)
    
    if is_valid:
        print("Token is valid!")
        print("Payload:", payload)
    else:
        print("Token verification failed")