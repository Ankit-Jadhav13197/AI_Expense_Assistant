# api/routers/ml_routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from api.ml.classifier import ExpenseClassifier

router = APIRouter(prefix="/ml", tags=["ml"])
cls = ExpenseClassifier()  

class PredictRequest(BaseModel):
    description: str

class PredictResponse(BaseModel):
    category: str
    probabilities: list  

@router.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
    desc = req.description
    if not desc or not desc.strip():
        raise HTTPException(status_code=400, detail="Empty description")
    cat = cls.predict(desc)
    probs = cls.predict_proba(desc)
    # Convert probabilities to list of [label, float]
    probs_list = [[label, float(prob)] for label, prob in probs]
    return {"category": cat, "probabilities": probs_list}
