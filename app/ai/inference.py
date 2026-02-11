import joblib
import pandas as pd

def score_links(model_path: str, X: pd.DataFrame) -> pd.DataFrame:
    clf = joblib.load(model_path)
    p = clf.predict_proba(X)[:, 1]
    out = X.copy()
    out["confidence"] = p
    out["strength_score"] = (p * 100.0).round(2)
    return out
