import json
from google.adk.tools import ToolContext
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmResponse, LlmRequest
from typing import Optional

from trade_utils import *
from strategies import *

def my_before_model_logic(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    callback_context.state['portfolio'] = dict()
    callback_context.state['watchlist'] = dict()
    # ... your custom logic here ...
    return None # Allow the model call to proceed


def run_strategy_1(tool_context: ToolContext, n: int=10):
  """
  Returns the top `n` stocks which are closest to their 52-week low, thus being suitable for a long-term investment.

  Args:
    n: The number of stocks to fetch the data for.
  """
  return topn_closest_to_52w_low(n=n)

def run_strategy_2(tool_context: ToolContext, n: int=10):
  """
  Returns the top `n` stocks with the highest gap-up and gap-down percentages respectively. These are suitable for short-term or intraday investments.

  Args:
    n: The number of stocks to fetch the data for each (gap-up and gap-down).
  """
  return get_top_gap_up_down(top_n=n)

def get_price(tool_context: ToolContext, ticker: str):
    """
    Returns the current price of the given stock.

    Args:
      ticker: The ticker symbol of the stock.
    """
    return get_current_price(ticker)


def update_watchlist(tool_context: ToolContext, ticker: str, amount: float, direction: str):
  """
  Updates the watchlist. Alerts the user automatically...
  1. Once the stock price drops below the amount (if direction is 'below').
  2. Once the stock price exceeds the amount (if the direction is 'above').

  Args:
    ticker: The ticker of the stock to update in the watchlist.
    amount: The amount at which to set the alert point.
    direction: Determines the alert condition. Must be 'above' or 'below'.
  """

  watchlist = tool_context.state['watchlist']
  if watchlist.get(ticker, {}):
    watchlist[ticker][direction] = amount
  else:
    watchlist[ticker] = {direction:amount}
  tool_context.state['watchlist'] = watchlist
  return {"status":"success", "message":f"watchlist updated"}

def remove_from_watchlist(tool_context: ToolContext, ticker: str):
  """
  Removes the specified stock from the watchlist.

  Args:
    ticker: The ticker of the stock to remove from the watchlist.
  """
  try:
    watchlist = tool_context.state['watchlist']
    bounds = watchlist.pop(ticker)
    tool_context.state['watchlist'] = watchlist
    return {"status":"success", "message":f"{ticker} stock has been removed from the watchlist"}
  except:
    return {"status":"error", "message":f"{ticker} is not in your watchlist"}

def buy_stock(tool_context: ToolContext, ticker: str, quantity: int):
  """
  Buys the specified number of the given stock.

  Args:
    ticker: The ticker symbol of the stock to purchase.
    quantity: The quantity of the stock to purchase.
  """
  buy_response = buy(quantity, ticker)
  if buy_response['status'] == 'error':
    return buy_response
  portfolio = tool_context.state['portfolio']
  if ticker in portfolio:
    portfolio[ticker] = portfolio[ticker] + quantity
    tool_context.state['portfolio'] = portfolio
  else:
    portfolio[ticker] = quantity
    tool_context.state['portfolio'] = portfolio
  return {"status":"success", "message":f"successfully purchased {quantity} {ticker} stocks"}

def sell_stock(tool_context: ToolContext, ticker: str, quantity: int):
  """
  Buys the specified number of the given stock.

  Args:
    ticker: The ticker symbol of the stock to purchase.
    quantity: The quantity of the stock to purchase.
  """
  portfolio = tool_context.state['portfolio']
  owned = portfolio.get(ticker, 0) - quantity
  if owned < 0:
    return {"status":"error", "message":f"you do not own enough {ticker} stocks"}
  sell_response = sell(quantity, ticker)
  if sell_response['status'] == 'error':
    return sell_response
  if owned == 0:
    quantity = portfolio.pop(ticker)
  else:
    portfolio[ticker] = owned
  tool_context.state['portfolio'] = portfolio
  return {"status":"success", "message":f"successfully sold {quantity} {ticker} stocks"}
