# api/ml/classifier.py
import os
from pathlib import Path
import joblib
from typing import Optional

BASE_DIR = Path(__file__).resolve().parent
MODEL_PATH = BASE_DIR.parent.parent / "ml" / "expense_classifier.pkl"

class ExpenseClassifier:
    def __init__(self, model_path: Optional[str] = None):
        path = model_path or MODEL_PATH
        if not Path(path).exists():
            raise FileNotFoundError(f"Model not found at {path}. Train it with scripts/train_classifier.py")
        self.pipeline = joblib.load(path)

    def predict(self, text: str) -> str:
        # text -> single predicted category label (string)
        pred = self.pipeline.predict([text])[0]
        return str(pred)

    def predict_proba(self, text: str):
        # returns list of (label, probability)
        probs = self.pipeline.predict_proba([text])[0]
        labels = self.pipeline.classes_
        return list(zip(labels, probs))
