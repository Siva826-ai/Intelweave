import pandas as pd

def temporal_features(df: pd.DataFrame) -> pd.DataFrame:
    t = pd.to_datetime(df["timestamp"], errors="coerce")
    out = pd.DataFrame(index=df.index)
    out["hour"] = t.dt.hour.fillna(-1).astype(int)
    out["dow"] = t.dt.dayofweek.fillna(-1).astype(int)
    out["is_night"] = out["hour"].between(0, 5).astype(int)
    return out
