import logging
import os
import secrets

from dotenv import get_key, load_dotenv

load_dotenv(
    verbose=True,
)


class Config:
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./test.db")

    SECRET_KEY = os.getenv("SECRET_KEY")
    if not SECRET_KEY:
        SECRET_KEY = secrets.token_hex(32)
        logging.warning(
            "SECRET_KEY not found in environment variables. "
            "Using temporary key - tokens will be invalidated on restart. "
            "Set SECRET_KEY in .env file for persistent authentication."
        )

    ROOT_USER_EMAIL = os.getenv("ROOT_USER_EMAIL", "admin@example.com")
    ROOT_USER_PASSWORD = os.getenv("ROOT_USER_PASSWORD", "admin")

    PM_USER_EMAIL = os.getenv("PM_USER_EMAIL", "pm@example.com")
    PM_USER_PASSWORD = os.getenv("PM_USER_PASSWORD", "supersecretpassword")

    HR_USER_EMAIL = os.getenv("HR_USER_EMAIL", "hr@example.com")
    HR_USER_PASSWORD = os.getenv("HR_USER_PASSWORD", "supersecretpassword")

    EMPLOYEE_USER_EMAIL = os.getenv("EMPLOYEE_USER_EMAIL", "employee@example.com")
    EMPLOYEE_USER_PASSWORD = os.getenv("EMPLOYEE_USER_PASSWORD", "supersecretpassword")

    PROJECT_NAME = "soft-engg-project-sep-2025-se-SEP-25"
    PROJECT_DESCRIPTION = ""
    VERSION = "0.0.1"
    OPENAI_API_KEY = get_key(".env", "OPENAI_API_KEY")
    if OPENAI_API_KEY is not None:
        os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

    MODE = get_key(".env", "MODE")

    POSTGRES = {
        "user": get_key(".env", "POSTGRES_USER"),
        "password": get_key(".env", "POSTGRES_PASSWORD"),
        "host": get_key(".env", "POSTGRES_HOST"),
        "port": get_key(".env", "POSTGRES_PORT"),
        "db": get_key(".env", "POSTGRES_DB"),
    }
    DATABASE_URL = f"postgresql://{POSTGRES['user']}:{POSTGRES['password']}@{POSTGRES['host']}:{POSTGRES['port']}/{POSTGRES['db']}"
