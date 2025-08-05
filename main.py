from utils.fetch_data import get_price_data

start_date = "2023-01-01"
end_date = "2024-12-31"

ticker1 = "GC=F"       
ticker2 = "DX-Y.NYB"   


try:
    df1 = get_price_data(ticker1, start_date, end_date)
    df2 = get_price_data(ticker2, start_date, end_date)

    print(df1.head())
    print(df2.head())
except Exception as e:
    print(f"Error: {e}")
