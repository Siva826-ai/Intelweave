import pandas as pd
from sklearn.ensemble import IsolationForest

class AnomalyModel:
    def __init__(self, contamination: float = 0.02):
        self.model = IsolationForest(n_estimators=300, contamination=contamination, random_state=42)

    def fit(self, X: pd.DataFrame) -> None:
        self.model.fit(X)

    def score(self, X: pd.DataFrame) -> pd.DataFrame:
        raw = -self.model.decision_function(X)
        scaled = (raw - raw.min()) / (raw.max() - raw.min() + 1e-9)
        out = X.copy()
        out["anomaly_score"] = (scaled * 100.0).round(2)
        out["confidence"] = scaled.round(4)
        return out
