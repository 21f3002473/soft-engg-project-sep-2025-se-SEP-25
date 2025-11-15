from datetime import datetime, timedelta
from logging import getLogger
from typing import Optional

from app.config import Config
from app.database import User, get_session
from app.utils import current_utc_time
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlmodel import Session, select

logger = getLogger(__name__)

logger = getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

SECRET_KEY = Config.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_DAYS = 7


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


def query_user_by_email(email: str):
    session = next(get_session())
    statement = select(User).where(User.email == email)
    result = session.exec(statement)
    user = result.first()
    return user


def authenticate_user(email: str, password: str):
    user = query_user_by_email(email)
    if not user:
        return False
    if not user.verify_password(password):
        return False
    return user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = current_utc_time() + expires_delta
    else:
        expire = current_utc_time() + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if not token or len(token.strip()) == 0:
        logger.error("Empty token received")
        raise credentials_exception

    token_parts = token.split(".")
    if len(token_parts) != 3:
        logger.error(f"Invalid token format. Expected 3 parts, got {len(token_parts)}")
        raise credentials_exception

    if not token or len(token.strip()) == 0:
        logger.error("Empty token received")
        raise credentials_exception

    token_parts = token.split(".")
    if len(token_parts) != 3:
        logger.error(f"Invalid token format. Expected 3 parts, got {len(token_parts)}")
        raise credentials_exception

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
        logger.debug(f"Token data: {token_data}")
    except JWTError as e:
        logger.error(f"JWT decoding error: {str(e)}", exc_info=True)
        raise credentials_exception

    user = query_user_by_email(token_data.username)
    if user is None:
        logger.error(f"User not found for email: {token_data.username}")
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user
