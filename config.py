import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "default-secret-key")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/flask_api"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_TYPE = "filesystem"
    SESSION_PERMANENT = True
    PERMANENT_SESSION_LIFETIME = 3600 * 24 * 7
    PRODUCTION = os.getenv("ENVIRONMENT", "TESTING") == "PRODUCTION"
