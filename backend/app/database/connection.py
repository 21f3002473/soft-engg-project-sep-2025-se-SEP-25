from sqlmodel import SQLModel, Session, create_engine
from app.config import Config

engine = create_engine(
    Config.DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
)

def get_session():
    with Session(engine) as session:
        yield session
        
def init_db():
    import app.database.employee_models
    import app.database.hr_models
    import app.database.admin_models
    import app.database.product_manager_models
    SQLModel.metadata.create_all(engine)