import pandas as pd

def calculate_correlation(df1: pd.DataFrame, df2: pd.DataFrame) -> float:
   
    combined = pd.concat([df1, df2], axis=1, join='inner').dropna()

    if combined.shape[0] < 2:
        raise ValueError("Not enough overlapping data to compute correlation.")

    return combined.corr().iloc[0, 1]
