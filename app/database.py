from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import settings

engine = create_engine(
    url=settings.DATABASE_URL_psycopg,
    echo=True
)

Session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    with Session() as db:
        yield db
