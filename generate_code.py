from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM
import re

def get_api_code(user_input):
    sample_code = r"""from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

app = FastAPI()

# SQLAlchemy database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"  # Using SQLite for simplicity
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
# Dependency for database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# SQLAlchemy model
class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
# Create the database tables
Base.metadata.create_all(bind=engine)
# Pydantic schema for validation
class ItemBase(BaseModel):
    title: str
    description: str
class ItemCreate(ItemBase):
    pass
class ItemResponse(ItemBase):
    id: int
    class Config:
        orm_mode = True
# CRUD operations
@app.post("/items/", response_model=ItemResponse)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = Item(title=item.title, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
@app.get("/items/", response_model=list[ItemResponse])
def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    items = db.query(Item).offset(skip).limit(limit).all()
    return items
    """
    question_template = f"""
    You are an expert Python API developer. The user needs an API with the following requirements: {user_input}. 
    Generate the complete FastAPI code and nothing else. Ensure there are no syntax errors. Ensure to use double underscores for __tablename__. Do not use "Depends". Here is a sample: {sample_code}. Modify it according"""

    template = """Question: {question}

    Answer: Let's think step by step."""

    prompt = ChatPromptTemplate.from_template(template)
    model = OllamaLLM(model="llama3")
    chain = prompt | model
    result = chain.invoke({"question": question_template})
    print(result)

    return result

def extract_code(text):
    # Regular expression to capture code between triple backticks
    imports = """from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
"""

    text = text[text.find("from"):]
    text = text[:text.find("`")]

    return imports + text

if __name__ == "__main__":
    print(extract_code(get_api_code("API for storing and retrieving employee data")))