import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt


def get_price_data(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    df = yf.download(ticker, start=start_date, end=end_date)

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


def calculate_returns(price_df: pd.DataFrame) -> pd.DataFrame:
    returns = price_df.pct_change().dropna()
    return returns


def calculate_pearson_corr(returns1: pd.Series, returns2: pd.Series) -> float:
    return returns1.corr(returns2)


st.title("📈 Correlation Tracker")

st.markdown(
    """
    <style>
    .info-icon {
        display: inline-block;
        margin-left: 10px;
        position: relative;
        cursor: pointer;
        font-weight: bold;
        color: #0a84ff;
    }
    .info-icon:hover .tooltip {
        visibility: visible;
        opacity: 1;
    }
    .tooltip {
        visibility: hidden;
        width: 320px;
        background-color: rgba(0, 0, 0, 0.7);
        color: white;
        text-align: left;
        border-radius: 6px;
        padding: 10px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -160px;
        opacity: 0;
        transition: opacity 0.3s;
        font-size: 14px;
        line-height: 1.4;
    }
    .tooltip::after {
        content: "";
        position: absolute;
        top: 100%;
        left: 50%;
        margin-left: -5px;
        border-width: 5px;
        border-style: solid;
        border-color: rgba(0, 0, 0, 0.7) transparent transparent transparent;
    }
    </style>

    <span class="info-icon">&#9432;
      <span class="tooltip">
        We built this live correlation tracker to facilitate analysis of cross asset price movements and respective correlations. Being aware of the relationship between financial instruments is essential for different trading strategies (arbitrage; hedging; etc.)
      </span>
    </span>
    """,
    unsafe_allow_html=True,
)

st.write("""
Enter two asset tickers (Yahoo Finance format) and a date range to analyze their correlation.
""")

ticker1 = st.text_input("First ticker (e.g. GC=F for Gold)", value="GC=F").upper()
ticker2 = st.text_input("Second ticker (e.g. DX-Y.NYB for US Dollar Index)", value="DX-Y.NYB").upper()
start_date = st.date_input("Start date", value=pd.to_datetime("2023-01-01"))
end_date = st.date_input("End date", value=pd.to_datetime("today"))

if start_date >= end_date:
    st.error("Error: Start date must be before end date.")
else:
    try:
        price1 = get_price_data(ticker1, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        price2 = get_price_data(ticker2, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

        price_df = pd.concat([price1, price2], axis=1).dropna()

        returns_df = calculate_returns(price_df)

        rolling_corr = returns_df[ticker1].rolling(window=30).corr(returns_df[ticker2])

        pearson_corr = calculate_pearson_corr(returns_df[ticker1], returns_df[ticker2])

        st.subheader("📊 Rolling 30-Day Correlation")
        fig_corr, ax_corr = plt.subplots()
        ax_corr.plot(rolling_corr.index, rolling_corr, label='30-Day Rolling Correlation')
        ax_corr.axhline(0, color='gray', linestyle='--', linewidth=1)
        ax_corr.set_title(f"30-Day Rolling Correlation between {ticker1} and {ticker2}")
        ax_corr.set_ylabel("Correlation")
        ax_corr.tick_params(axis='x', labelsize=8)
        fig_corr.autofmt_xdate()
        st.pyplot(fig_corr)

        st.subheader("📎 Pearson Correlation Coefficient")
        st.metric(label="Correlation", value=f"{pearson_corr:.4f}")

        if st.button("Show Pearson Correlation Formula"):
            st.latex(r"r = \frac{\text{Cov}(X, Y)}{\sigma_X \cdot \sigma_Y}")

        st.subheader("💵 Price Chart (USD)")
        fig_price, ax_price = plt.subplots()
        ax_price.plot(price_df[ticker1], label=ticker1)
        ax_price.plot(price_df[ticker2], label=ticker2)
        ax_price.set_title(f"{ticker1} vs {ticker2} Prices in USD")
        ax_price.set_ylabel("Price (USD)")
        ax_price.tick_params(axis='x', labelsize=8)
        fig_price.autofmt_xdate()
        ax_price.legend()
        st.pyplot(fig_price)

    except Exception as e:
        st.error(f"An error occurred: {e}")
