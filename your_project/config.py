import os

JWT_SECRET = os.getenv("JWT_SECRET", "your_supabase_jwt_secret_key")
ALGORITHM = "HS256"
