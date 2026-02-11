from __future__ import annotations
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV

def train_link_strength(X: pd.DataFrame, y: pd.Series, out_path: str) -> dict:
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    base = HistGradientBoostingClassifier(max_depth=6, learning_rate=0.08)
    clf = CalibratedClassifierCV(base, method="isotonic", cv=3)
    clf.fit(X_train, y_train)
    probs = clf.predict_proba(X_test)[:, 1]
    auc = roc_auc_score(y_test, probs)
    joblib.dump(clf, out_path)
    return {"auc": float(auc), "model_path": out_path}
