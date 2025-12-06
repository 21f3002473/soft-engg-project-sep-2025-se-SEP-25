from app.config import Config
from app.database.connection import engine
from app.database.employee_models import RoleEnum, User
from sqlmodel import Session, select


def create_root_user():
    root_email = Config.ROOT_USER_EMAIL
    root_password = Config.ROOT_USER_PASSWORD

    with Session(engine) as session:
        statement = select(User).where(User.email == root_email)
        result = session.exec(statement)
        existing_user = result.first()

        if existing_user:
            print("Root user already exists.")
            return

        password_hash, salt = User.hash_password(root_password)
        root_user = User(
            email=root_email,
            name="root",
            password_hash=password_hash,
            salt=salt,
            role=RoleEnum.ROOT,
        )
        session.add(root_user)
        session.commit()
        print("Root user created.")

    pm_email = Config.PM_USER_EMAIL
    pm_password = Config.PM_USER_PASSWORD

    with Session(engine) as session:
        statement = select(User).where(User.email == pm_email)
        result = session.exec(statement)
        existing_user = result.first()

        if existing_user:
            print("PM user already exists.")
            return

        password_hash, salt = User.hash_password(pm_password)
        pm_user = User(
            email=pm_email,
            name="pm",
            password_hash=password_hash,
            salt=salt,
            role=RoleEnum.PRODUCT_MANAGER,
        )
        session.add(pm_user)
        session.commit()
        print("PM user created.")

    hr_email = Config.HR_USER_EMAIL
    hr_password = Config.HR_USER_PASSWORD

    with Session(engine) as session:
        statement = select(User).where(User.email == hr_email)
        result = session.exec(statement)
        existing_user = result.first()

        if existing_user:
            print("HR user already exists.")
            return

        password_hash, salt = User.hash_password(hr_password)
        hr_user = User(
            email=hr_email,
            name="hr",
            password_hash=password_hash,
            salt=salt,
            role=RoleEnum.HUMAN_RESOURCE,
        )
        session.add(hr_user)
        session.commit()
        print("HR user created.")

    employee_email = Config.EMPLOYEE_USER_EMAIL
    employee_password = Config.EMPLOYEE_USER_PASSWORD

    with Session(engine) as session:
        statement = select(User).where(User.email == employee_email)
        result = session.exec(statement)
        existing_user = result.first()

        if existing_user:
            print("Employee user already exists.")
            return

        password_hash, salt = User.hash_password(employee_password)
        employee_user = User(
            email=employee_email,
            name="employee",
            password_hash=password_hash,
            salt=salt,
            role=RoleEnum.EMPLOYEE,
        )
        session.add(employee_user)
        session.commit()
        print("Employee user created.")
