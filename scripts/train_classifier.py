# scripts/train_classifier.py
import pandas as pd
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.naive_bayes import MultinomialNB
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
import re
import argparse

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
MODEL_DIR = PROJECT_ROOT / "ml"
MODEL_DIR.mkdir(exist_ok=True)

def clean_text(s: str) -> str:
    s = s.lower()
    s = re.sub(r"[^a-z0-9\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def load_data(csv_path: Path):
    df = pd.read_csv(csv_path)
    # expected columns: description, category
    df = df.dropna(subset=["description", "category"])
    df["description_clean"] = df["description"].astype(str).apply(clean_text)
    return df

def train(csv_path: Path, save_path: Path):
    df = load_data(csv_path)
    X = df["description_clean"]
    y = df["category"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1,2), min_df=2)),
        ("clf", MultinomialNB())
    ])

    pipeline.fit(X_train, y_train)
    preds = pipeline.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print("Test accuracy:", acc)
    print(classification_report(y_test, preds))

    joblib.dump(pipeline, save_path)
    print(f"Saved model to {save_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=str, default=str(DATA_DIR / "labeled_expenses.csv"))
    parser.add_argument("--out", type=str, default=str(MODEL_DIR / "expense_classifier.pkl"))
    args = parser.parse_args()
    train(Path(args.csv), Path(args.out))
