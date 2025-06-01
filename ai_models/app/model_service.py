# ai_models/app/model_service.py
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from interfaces.model_service import TextCorrectionService

class GrammarCorrector(TextCorrectionService):
    def __init__(self):
        self.model_name = "dreuxx26/Multilingual-grammar-Corrector-using-mT5-small"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(self.model_name)

    def correct(self, text: str) -> str:
        input_text = f"gec: {text}"
        inputs = self.tokenizer(input_text, return_tensors="pt", padding=True, truncation=True)
        outputs = self.model.generate(**inputs, max_new_tokens=64)
        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)