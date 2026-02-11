import pandas as pd

def load_file_to_df(path: str) -> pd.DataFrame:
    p = path.lower()
    if p.endswith(".csv"):
        return pd.read_csv(path)
    if p.endswith(".xlsx"):
        return pd.read_excel(path)
    raise ValueError("Unsupported file format")
