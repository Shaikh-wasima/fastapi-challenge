import os

from dotenv import load_dotenv

load_dotenv()


def get_env(name: str, default: str | None = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing required env var: {name}")
    return value


MONGODB_URL = get_env("MONGODB_URL", "mongodb://localhost:27017")
MONGODB_DB_NAME = get_env("MONGODB_DB_NAME", "challenge_db")
MONGODB_CREATE_INDEXES = get_env("MONGODB_CREATE_INDEXES", "true").lower() == "true"
SECRET_KEY = get_env("SECRET_KEY", "CHANGE_ME_IN_PROD")
ALGORITHM = get_env("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(get_env("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))
