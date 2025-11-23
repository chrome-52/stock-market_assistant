import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import requests

def get_nasdaq_100():
    url = "https://stockanalysis.com/list/nasdaq-100-stocks/"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    html = requests.get(url, headers=headers).text

    df = pd.read_html(html)[0]
    return df["Symbol"].tolist()

# Example list of NASDAQ tickers
try: 
    nasdaq_tickers = get_nasdaq_100()
except:
    nasdaq_tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA",
    "META", "NVDA", "PYPL", "CSCO", "INTC"
    ]

def fetch_1year_data(ticker):
    end = datetime.datetime.today()
    start = end - datetime.timedelta(days=365)
    df = yf.download(ticker, start=start, end=end, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]  # keep only the second level (Open, High, Low, etc.)
    df = df.reset_index()
    df["Ticker"] = ticker
    if df.empty:
        print(f"Skipping {ticker}: no data")
        return None
    return df

def topn_closest_to_52w_low(tickers=nasdaq_tickers, n=10):
    try:    
        results = []

        for ticker in tickers:
            df = fetch_1year_data(ticker)
            if df is None:
                continue

            # Make sure we take scalar values
            low_52w = df["Close"].min()  # scalar
            current_price = df["Close"].iloc[-1]  # scalar

            pct_above_low = (current_price - low_52w) / low_52w * 100

            results.append({
                "Ticker": ticker,
                "CurrentPrice": current_price,
                "52WeekLow": low_52w,
                "PercentAboveLow": pct_above_low
            })

        res_df = pd.DataFrame(results)
        res_df = res_df.sort_values(by="PercentAboveLow", ascending=True)
        return res_df.reset_index(drop=True).to_dict(orient="records")[:n]
    except Exception as e:
        return {"error":str(e)}

def get_last_two_days_data(ticker):
    """
    Fetches last 3 calendar days of data (covers weekends/holidays)
    and returns the last 2 available trading days.
    """
    end = datetime.datetime.today()
    start = end - datetime.timedelta(days=5)  # buffer for weekends
    df = yf.download(ticker, start=start, end=end, progress=False)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[0] for col in df.columns]  # keep only the second level (Open, High, Low, etc.)
    df = df.reset_index()
    df["Ticker"] = ticker
    if len(df) < 2:
        return None
    return df.tail(2)

def calculate_gaps(tickers):
    """
    Calculates gap percentage for each ticker.
    """
    gap_data = []
    for ticker in tickers:
        df = get_last_two_days_data(ticker)
        if df is None:
            continue
        try:
            yesterday_close = df["Close"].iloc[-2]
            today_open = df["Open"].iloc[-1]
            gap_pct = (today_open - yesterday_close) / yesterday_close * 100
            gap_data.append({"Ticker": ticker, "GapPercent": gap_pct})
        except Exception as e:
            print(f"Skipping {ticker}: {e}")
            continue

    df_gaps = pd.DataFrame(gap_data)
    return df_gaps

def get_top_gap_up_down(tickers=nasdaq_tickers, top_n=10):
    """
    Returns top N gap-up and gap-down stocks.
    """
    try:    
        df_gaps = calculate_gaps(tickers)

        if df_gaps.empty:
            print("No data found.")
            return None, None

        top_gap_up = df_gaps.sort_values(by="GapPercent", ascending=False).head(top_n).reset_index(drop=True).to_dict(orient="records")
        top_gap_down = df_gaps.sort_values(by="GapPercent", ascending=True).head(top_n).reset_index(drop=True).to_dict(orient="records")

        return {"Top Gap-Up": top_gap_up, 
                "Top Gap-Down": top_gap_down}
    except Exception as e:
        return {"error":str(e)}

        
if __name__ == "__main__":
    up, down = get_top_gap_up_down()
    print(up, down)
    print(top10_closest_to_52w_low())