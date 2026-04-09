from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama.llms import OllamaLLM

# -------------------------------------------------------
# This file talks to the Ollama AI and asks it to write
# FastAPI code based on what the user typed.
# -------------------------------------------------------

SAMPLE_CODE = r"""
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel

app = FastAPI()

SQLALCHEMY_DATABASE_URL = "sqlite:///./app.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Item(Base):
    __tablename__ = "items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)

Base.metadata.create_all(bind=engine)

class ItemBase(BaseModel):
    title: str
    description: str

class ItemCreate(ItemBase):
    pass

class ItemResponse(ItemBase):
    id: int
    class Config:
        orm_mode = True

@app.post("/items/", response_model=ItemResponse)
def create_item(item: ItemCreate, db: Session = Depends(get_db)):
    db_item = Item(title=item.title, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@app.get("/items/", response_model=list[ItemResponse])
def read_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return db.query(Item).offset(skip).limit(limit).all()
"""

FIXED_IMPORTS = """from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
"""


def get_api_code(user_input: str) -> str:
    """
    Sends the user's prompt to Ollama (Llama3) and gets back
    Python FastAPI code. Returns the raw AI response.
    """
    instruction = f"""
    You are an expert Python API developer.
    The user needs an API with the following requirements: {user_input}

    Rules you MUST follow:
    - Generate ONLY Python code. No explanations, no markdown, no backticks.
    - Use double underscores for __tablename__
    - Use SQLite as the database
    - Include full CRUD operations (create + read at minimum)
    - Start your response directly with: from fastapi import

    Here is a complete example to follow as a template:
    {SAMPLE_CODE}

    Now generate code for: {user_input}
    Start directly with the imports.
    """

    template = "Question: {question}\nAnswer:"
    prompt = ChatPromptTemplate.from_template(template)
    model = OllamaLLM(model="llama3")
    chain = prompt | model

    result = chain.invoke({"question": instruction})
    return result


def extract_code(raw_text: str) -> str:
    """
    Cleans up the AI's response.
    The AI sometimes writes English sentences before/after the code.
    This function strips all that and keeps only the Python code.
    """
    # Find where the actual Python code starts
    start_markers = ["from fastapi", "import fastapi", "from sqlalchemy"]
    start_index = len(raw_text)  # default: end of string (nothing found)

    for marker in start_markers:
        idx = raw_text.lower().find(marker.lower())
        if idx != -1 and idx < start_index:
            start_index = idx

    if start_index == len(raw_text):
        # AI didn't generate proper code — return a helpful placeholder
        return FIXED_IMPORTS + '\napp = FastAPI()\n\n# AI could not generate code. Try a more specific prompt.\n'

    code = raw_text[start_index:]

    # Remove any trailing markdown backticks the AI might have added
    if "```" in code:
        code = code[:code.find("```")]

    # Always ensure the standard imports are at the top
    return FIXED_IMPORTS + "\n" + code.strip()
