from sqlmodel import Session, SQLModel, create_engine

DATABASE_URL = "postgresql://postgres:test@localhost:5432/alma"

engine = create_engine(DATABASE_URL, echo=False)  # Set to False in production


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_db():
    with Session(engine) as session:
        yield session
