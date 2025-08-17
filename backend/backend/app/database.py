# backend/app/database.py
from sqlalchemy import create_engine
#from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# ATENÇÃO: Substitua com suas credenciais reais.
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:8940@127.0.0.1/process_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependência para obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()