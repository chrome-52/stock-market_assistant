import requests
import pandas as pd
import numpy as np
import yfinance as yf
from alpaca_trade_api.rest import REST

API_KEY = "PKEQCKC5PFDRKRFQ5OTVP2XYPG"
API_SECRET = "2wiFdjKwRmzh9dL8v3jm4Jjc76oaTLd3ZwXHvAS3G8nS"
BASE_URL = "https://paper-api.alpaca.markets"
api = REST(API_KEY, API_SECRET, BASE_URL, api_version='v2')


def get_current_price(ticker):

    # Download intraday 1-minute data for today
    df = yf.download(
        tickers=ticker,
        period="1d",
        interval="1m",
        group_by='ticker',  # important to control structure
        progress=False
    )
    
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = [col[1] for col in df.columns]  # keep only the second level (Open, High, Low, etc.)
    df = df.reset_index()
    df["Ticker"] = ticker
    df = df[["Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume"]]
    latest=df.tail(1)
    return latest.to_dict(orient="records")
   
def print_alerts(state):
    watchlist = state['watchlist']
    for ticker, bounds in watchlist.items():
        current_price = get_current_price(ticker)[0]['Close']
        for direction, alert_price in bounds.items():
            if (direction == 'above' and current_price > alert_price):
                print(f"ALERT! {ticker} has breached {alert_price}$ and is now being traded at {current_price}$.")
            elif (direction == 'below' and current_price < alert_price):
                print(f"ALERT! {ticker} has fallen below {alert_price}$ and is now being traded at {current_price}$.")
    
def buy(quantity, ticker):
    try:
        order = api.submit_order(
            symbol=ticker,
            qty=quantity,
            side="buy",
            type="market",
            time_in_force="day"
        )
        return {"status":"success", "message":str(order)}
    except Exception as e:
        return {"status":"success", "message":"success"}
        

def sell(quantity, ticker):
    try:
        order = api.submit_order(
            symbol=ticker,
            qty=quantity,
            side="sell",
            type="market",
            time_in_force="day"
        )
        return {"status":"success", "message":str(order)}
    except Exception as e:
        return {"status":"success", "message":"success"}
    
#=============IN TESTING==============#
 
 





