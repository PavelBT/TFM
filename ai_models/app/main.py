# ai_models/app/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from app.model_service import GrammarCorrector

app = FastAPI()
model = GrammarCorrector()

class TextIn(BaseModel):
    text: str

@app.post("/correct")
def correct_text(data: TextIn):
    result = model.correct(data.text)
    return {"corrected": result}
