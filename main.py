# main.py
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from Backend.Assignment import get_answer

app = FastAPI()

# Allow CORS for frontend (React or testing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    question: str

@app.get("/")
def home():
    return {"message": "RAG API is running"}

@app.post("/ask")
def ask_question(query: Query):
    answer = get_answer(query.question)
    return {"question": query.question, "answer": answer}
