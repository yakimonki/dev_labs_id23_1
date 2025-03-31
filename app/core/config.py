import os
from dotenv import load_dotenv

load_dotenv()

JWT_SECRET = os.getenv("JWT_SECRET", "your_jwt_secret")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")
