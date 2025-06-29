# database.py
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///estoque.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine)

Base = declarative_base()

class Item(Base):
    __tablename__ = "estoque"
    id = Column(Integer, primary_key=True, index=True)
    categoria = Column(String, index=True)
    item = Column(String, index=True)
    quantidade = Column(Integer)
    preco = Column(Float)

Base.metadata.create_all(bind=engine)
