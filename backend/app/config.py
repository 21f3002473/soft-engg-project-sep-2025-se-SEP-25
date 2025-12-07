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

    REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", None)
    REDIS_URL = (
        f"redis://:{REDIS_PASSWORD}@{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
        if REDIS_PASSWORD
        else f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}"
    )

    CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", REDIS_URL)
    CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", REDIS_URL)

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
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

    GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
    if GROQ_API_KEY:
        os.environ["GROQ_API_KEY"] = GROQ_API_KEY

    MODE = get_key(".env", "MODE")

    POSTGRES = {
        "user": get_key(".env", "POSTGRES_USER"),
        "password": get_key(".env", "POSTGRES_PASSWORD"),
        "host": get_key(".env", "POSTGRES_HOST"),
        "port": get_key(".env", "POSTGRES_PORT"),
        "db": get_key(".env", "POSTGRES_DB"),
    }
    DATABASE_URL = f"postgresql://{POSTGRES['user']}:{POSTGRES['password']}@{POSTGRES['host']}:{POSTGRES['port']}/{POSTGRES['db']}"
    print("DATABASE_URL:", DATABASE_URL)

    SMTP_HOST = os.getenv("SMTP_HOST", "localhost")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "1025"))
    SMTP_USER = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
    SMTP_FROM_EMAIL = os.getenv("SMTP_FROM_EMAIL", "noreply@example.com")
    SMTP_FROM_NAME = os.getenv("SMTP_FROM_NAME", "Project Management System")

    MAILHOG_UI_URL = os.getenv("MAILHOG_UI_URL", "http://localhost:8025")
