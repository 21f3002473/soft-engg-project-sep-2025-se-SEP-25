from app.config import Config
from sqlmodel import Session, select
from app.database.connection import engine
from app.database.employee_models import Users

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