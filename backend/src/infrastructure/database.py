from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.src.settings import settings

engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
print(settings.database_url)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
