import hashlib
import hmac
import secrets
import time
from os import name
from typing import Annotated

from app.config import Config
from fastapi import Depends, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select


class Users(SQLModel, table=True):
    id: int | None = Field(
        default=None,
        primary_key=True,
    )
    email: str = Field(
        index=True,
    )
    name: str = Field(
        index=True,
        nullable=False,
    )
    password_hash: str = Field(
        index=False,
        nullable=False,
    )
    salt: str = Field(default_factory=lambda: secrets.token_hex(16), nullable=False)
    role: str = Field(
        default="employee",
        index=True,
        nullable=False,
    )

    def generate_token(self) -> str:

        expiry = int(time.time()) + 86400
        token_data = f"{self.id}:{self.email}:{expiry}"
        signature = hmac.new(
            Config.SECRET_KEY.encode(), token_data.encode(), hashlib.sha256
        ).hexdigest()
        return f"{token_data}:{signature}"

    def verify_password(self, password: str) -> bool:
        password_hash = hashlib.sha256(f"{password}{self.salt}".encode()).hexdigest()
        return hmac.compare_digest(self.password_hash, password_hash)

    @staticmethod
    def hash_password(password: str, salt: str = None) -> tuple[str, str]:

        if salt is None:
            salt = secrets.token_hex(16)
        password_hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
        return password_hash, salt


engine = create_engine(
    Config.DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
)


def get_session():
    with Session(engine) as session:
        yield session


def create_root_user():
    root_email = Config.ROOT_USER_EMAIL
    root_password = Config.ROOT_USER_PASSWORD

    with Session(engine) as session:
        statement = select(Users).where(Users.email == root_email)
        result = session.exec(statement)
        existing_user = result.first()

        if existing_user:
            print("Root user already exists.")
            return

        password_hash, salt = Users.hash_password(root_password)
        root_user = Users(
            email=root_email,
            name="root",
            password_hash=password_hash,
            salt=salt,
            role="root",
        )
        session.add(root_user)
        session.commit()
        print("Root user created.")

    # pm
    pm_email = Config.PM_USER_EMAIL
    pm_password = Config.PM_USER_PASSWORD

    with Session(engine) as session:
        statement = select(Users).where(Users.email == pm_email)
        result = session.exec(statement)
        existing_user = result.first()

        if existing_user:
            print("PM user already exists.")
            return

        password_hash, salt = Users.hash_password(pm_password)
        pm_user = Users(
            email=pm_email,
            name="pm",
            password_hash=password_hash,
            salt=salt,
            role="pm",
        )
        session.add(pm_user)
        session.commit()
        print("PM user created.")
        
        
    # hr
    hr_email = Config.HR_USER_EMAIL
    hr_password = Config.HR_USER_PASSWORD
    
    with Session(engine) as session:
        statement = select(Users).where(Users.email == hr_email)
        result = session.exec(statement)
        existing_user = result.first()
        
        if existing_user:
            print("HR user already exists.")
            return
        
        password_hash, salt = Users.hash_password(hr_password)
        hr_user = Users(
            email=hr_email,
            name="hr",
            password_hash=password_hash,
            salt=salt,
            role="hr",
        )
        session.add(hr_user)
        session.commit()
        print("HR user created.")
        
    # employee
    employee_email = Config.EMPLOYEE_USER_EMAIL
    employee_password = Config.EMPLOYEE_USER_PASSWORD

    with Session(engine) as session:
        statement = select(Users).where(Users.email == employee_email)
        result = session.exec(statement)
        existing_user = result.first()

        if existing_user:
            print("Employee user already exists.")
            return

        password_hash, salt = Users.hash_password(employee_password)
        employee_user = Users(
            email=employee_email,
            name="employee",
            password_hash=password_hash,
            salt=salt,
            role="employee",
        )
        session.add(employee_user)
        session.commit()
        print("Employee user created.")

if __name__ == "__main__":
    SQLModel.metadata.create_all(engine)
