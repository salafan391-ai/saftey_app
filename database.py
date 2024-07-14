from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Update this with your actual database URL
DATABASE_URL = 'sqlite:///safety_db.db'

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def db_session():
    with next(get_db()) as db:
        return db
