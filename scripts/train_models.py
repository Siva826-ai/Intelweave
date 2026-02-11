"""Example training script.
Replace the toy dataset with your labelled relationship dataset.
"""
import os
import pandas as pd
from app.ai.training import train_link_strength

os.makedirs("artifacts", exist_ok=True)

# Toy example data (replace!)
X = pd.DataFrame({
    "calls_count": [1, 5, 20, 2, 40, 3],
    "unique_days": [1, 2, 10, 1, 15, 1],
    "co_location_hits": [0, 1, 8, 0, 12, 0],
})
y = pd.Series([0, 0, 1, 0, 1, 0])

result = train_link_strength(X, y, "artifacts/link_strength_model.joblib")
print(result)
