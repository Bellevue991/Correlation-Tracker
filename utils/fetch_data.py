import yfinance as yf
import pandas as pd

def fetch_adjusted_close(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    df = yf.download(ticker, start=start_date, end=end_date)

    print(f"\nRaw data for {ticker}:\n", df.head())
    print(f"\nColumns: {df.columns}")

    if df.empty:
        raise ValueError(f"No data found for ticker: {ticker}")

    
    if isinstance(df.columns, pd.MultiIndex):
        for price_type in ['Adj Close', 'Close']:
            for col in df.columns:
                if col[0] == price_type:
                    return df[col].to_frame(name=ticker)
        raise ValueError(f"No usable price columns found in multi-index for {ticker}.")
    
    if 'Adj Close' in df.columns:
        return df[['Adj Close']].rename(columns={'Adj Close': ticker})
    elif 'Close' in df.columns:
        return df[['Close']].rename(columns={'Close': ticker})
    else:
        raise ValueError(f"No usable price columns found for {ticker}. Columns: {df.columns}")


get_price_data = fetch_adjusted_close
