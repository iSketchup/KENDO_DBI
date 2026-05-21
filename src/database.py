from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

SQLALCHEMY_DATABASE_URL = "sqlite:///meine_app.db"

# Engine erstellen
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Session Factory erstellen
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Basisklasse für die Modelle
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
