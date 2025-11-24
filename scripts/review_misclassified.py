# scripts/review_misclassified.py
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MIS = ROOT / "data" / "misclassified_log.csv"
LABELED = ROOT / "data" / "labeled_expenses.csv"

if not MIS.exists():
    print("No misclassification log found.")
else:
    df = pd.read_csv(MIS)
    # show summary
    print(df.groupby("predicted").size().sort_values(ascending=False).head())
    # Example: append rows where actual exists into labeled CSV for retraining
    df_valid = df[df["actual"].notnull() & (df["actual"] != "")]
    if not df_valid.empty:
        labeled = pd.read_csv(LABELED) if LABELED.exists() else pd.DataFrame(columns=["description", "category"])
        to_add = df_valid[["description", "actual"]].rename(columns={"actual": "category"})
        merged = pd.concat([labeled, to_add], ignore_index=True)
        merged.to_csv(LABELED, index=False)
        print(f"Appended {len(to_add)} rows to {LABELED}")
