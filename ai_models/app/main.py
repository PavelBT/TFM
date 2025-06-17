from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict

from app.model_service import GrammarCorrector
from app.refiner_service import CombinedRefiner

app = FastAPI()
corrector = GrammarCorrector()
refiner = CombinedRefiner()

class TextIn(BaseModel):
    text: str

class FieldsIn(BaseModel):
    fields: Dict[str, str]

@app.post("/correct")
def correct_text(data: TextIn):
    result = corrector.correct(data.text)
    return {"corrected": result}

@app.post("/refine")
def refine_fields(data: FieldsIn):
    refined = refiner.refine(data.fields)
    return {"fields": refined}

