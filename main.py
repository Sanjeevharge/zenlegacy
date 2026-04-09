from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

app = FastAPI()

SQLALCHEMY_DATABASE_URL = "sqlite:///./booklibrary.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Book(Base):
    __tablename__ = "books"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    author = Column(String, index=True)
    genre = Column(String, index=True)
    available_copies = Column(Float)

Base.metadata.create_all(bind=engine)

class BookBase(BaseModel):
    title: str
    author: str
    genre: str
    available_copies: float

class BookCreate(BookBase):
    pass

class BookResponse(BookBase):
    id: int
    class Config:
        orm_mode = True

@app.post("/books/", response_model=BookResponse)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    db_book = Book(title=book.title, author=book.author, genre=book.genre, available_copies=book.available_copies)
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.get("/books/", response_model=list[BookResponse])
def read_books(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Book).offset(skip).limit(limit).all()