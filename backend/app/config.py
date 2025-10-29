import logging
import os
import secrets

from dotenv import get_key, load_dotenv

# load env keys

load_dotenv(
    verbose=True,
)


class Config:
    # Database settings
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

    # Security
    SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_hex(32))

    # Root user
    ROOT_USER_EMAIL = os.getenv("ROOT_USER_EMAIL", "admin@example.com")
    ROOT_USER_PASSWORD = os.getenv("ROOT_USER_PASSWORD", "admin")

    PROJECT_NAME = "soft-engg-project-sep-2025-se-SEP-25"
    PROJECT_DESCRIPTION = ""
    VERSION = "0.0.1"
    GROQ_API_KEY = get_key(".env", "GROQ_API_KEY")
    if GROQ_API_KEY is not None:
        os.environ["GROQ_API_KEY"] = GROQ_API_KEY

    POSTGRES = {
        "user": get_key(".env", "POSTGRES_USER"),
        "password": get_key(".env", "POSTGRES_PASSWORD"),
        "host": get_key(".env", "POSTGRES_HOST"),
        "port": get_key(".env", "POSTGRES_PORT"),
        "db": get_key(".env", "POSTGRES_DB"),
    }
    DATABASE_URL = f"postgresql://{POSTGRES['user']}:{POSTGRES['password']}@{POSTGRES['host']}:{POSTGRES['port']}/{POSTGRES['db']}"
