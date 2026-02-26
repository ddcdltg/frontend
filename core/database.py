from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# Credenciales de la BD
DB_USER = "dali"
DB_PASSWORD = "12345"
DB_HOST = "127.0.0.1"
DB_PORT = "3306"
DB_NAME = "backend_db"  

DATABASE_URL = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    "?charset=utf8mb4"
)

# Engine
engine = create_engine(
    DATABASE_URL,
    echo=True,          # muestra SQL en consola (opcional)
    pool_pre_ping=True  # evita conexiones muertas
)

# Session
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

# Base
Base = declarative_base()