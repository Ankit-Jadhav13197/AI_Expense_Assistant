# tests/test_classifier.py
from api.ml.classifier import ExpenseClassifier

def test_predict():
    cls = ExpenseClassifier()
    sample = "coffee from starbucks"
    cat = cls.predict(sample)
    assert isinstance(cat, str)
