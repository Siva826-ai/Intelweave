import numpy as np
import pandas as pd

def psi(expected: pd.Series, actual: pd.Series, buckets: int = 10) -> float:
    expected = expected.dropna().astype(float)
    actual = actual.dropna().astype(float)
    breakpoints = np.quantile(expected, np.linspace(0, 1, buckets + 1))
    breakpoints[0], breakpoints[-1] = -np.inf, np.inf

    def dist(x):
        hist, _ = np.histogram(x, bins=breakpoints)
        pct = hist / max(hist.sum(), 1)
        return np.clip(pct, 1e-6, 1.0)

    e = dist(expected)
    a = dist(actual)
    return float(np.sum((a - e) * np.log(a / e)))
