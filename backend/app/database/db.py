from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
import os

# DATABASE_URL can be sqlite:///./sar_ai.db or postgres://... for production
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///./sar_ai.db')

engine_kwargs = {}
connect_args = {}
if DATABASE_URL.startswith('sqlite'):
    connect_args = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, connect_args=connect_args, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
