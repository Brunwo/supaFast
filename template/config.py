from dotenv import load_dotenv
import os

# Load environment variables from a .env file
load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET")
TEST_TOKEN = os.getenv("TEST_TOKEN")
ORIGINS = os.getenv("ORIGINS", "").split(",")

ALGORITHM = "HS256"