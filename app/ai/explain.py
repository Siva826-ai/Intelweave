from __future__ import annotations
import pandas as pd

def simple_contribution_explain(X_row: pd.Series, feature_weights: dict[str, float]) -> dict:
    contrib = {k: float(X_row.get(k, 0.0)) * float(w) for k, w in feature_weights.items()}
    top = sorted(contrib.items(), key=lambda kv: abs(kv[1]), reverse=True)[:6]
    return {"top_contributors": top, "note": "Heuristic explanation (not model-specific)."} 
