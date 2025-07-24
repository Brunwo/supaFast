
import jwt
from datetime import datetime, timedelta

# Configuration
SECRET_KEY = "your-jwt-secret-here"
USER_ID = "test-user-guest"
ROLE = "guest"
EMAIL = "guest@example.com"
EXPIRATION = datetime.utcnow() + timedelta(hours=1)

# Create the payload
payload = {
    "sub": USER_ID,
    "role": ROLE,
    "email": EMAIL,
    "exp": EXPIRATION,
    "is_anonymous": False
}

# Generate the token
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

print(token)
