from __future__ import annotations
import pandas as pd

def validate_cdr(df: pd.DataFrame) -> dict:
    required_cols = {"a_party", "b_party", "timestamp", "cell_id"}
    cols = set([str(c).lower() for c in df.columns])
    missing = sorted(list(required_cols - cols))
    completeness = 100.0 * (1.0 - (len(missing) / max(len(required_cols), 1)))

    null_rate = float(df.isna().mean().mean())
    time_parse_ok = 1.0
    try:
        pd.to_datetime(df["timestamp"], errors="raise")
    except Exception:
        time_parse_ok = 0.0

    validation_score = max(0.0, completeness - (null_rate * 50.0) + (time_parse_ok * 10.0))
    validation_score = min(100.0, validation_score)

    return {
        "missing_required_columns": missing,
        "null_rate": round(null_rate, 4),
        "time_parse_ok": bool(time_parse_ok),
        "validation_score": round(validation_score, 2),
    }
