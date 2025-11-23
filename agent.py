from google.adk.tools import AgentTool, google_search
from google.adk.agents import LlmAgent

from tools import *
from prompts import *


information_agent = LlmAgent(
    name="information_agent",
    model="gemini-2.0-flash",
    description="Provides information on the stocks owned by the user and/or the stocks being watched for the user.",
    instruction=portfolio_instruction
)
information_tool = AgentTool(information_agent)

ticker_agent = LlmAgent(
    name="ticker_agent",
    model="gemini-2.0-flash",
    description="Returns the ticker symbol for the stock.",
    instruction=ticker_instruction,
    tools=[google_search]
)
ticker_tool = AgentTool(ticker_agent)

# technical_analysis_agent = LlmAgent(
#     name="technical_analysis_agent",
#     model="gemini-2.0-flash",
#     description="Conducts technical analysis on a company.",
#     instruction=technical_instruction,
#     tools=[google_search]
# )
# technical_analysis_tool = AgentTool(technical_analysis_agent)

# sentiment_analysis_agent = LlmAgent(
#     name="sentiment_analysis_agent",
#     model="gemini-2.0-flash",
#     description="Conducts sentiment analysis on a market sector or stock.",
#     instruction=sector_instruction,
#     tools=[google_search]
# )
# sentiment_analysis_tool = AgentTool(sentiment_analysis_agent)

# analysis_agent = LlmAgent(
#     name="analysis_agent",
#     model="gemini-2.0-flash",
#     description="Uses tools to conduct technical analysis of companies or market sector analysis.",
#     instruction="""Your job is to coordinate agents which can either conduct technical analysis of a company or analyze sentiments on a market sector or stock. 
#     You can delegate to the following agents:
#     - technical_analysis_agent
#     - sentiment_analysis_agent
    
#     If you can not fulfill the user's request, redirect them back to the root_agent WITHOUT asking for the user's confirmation.""",
#     sub_agents=[technical_analysis_agent, sentiment_analysis_agent]
# )

transactions_agent = LlmAgent(
    name="transactions_agent",
    model="gemini-2.0-flash",
    description="Assists the user with stock transactions.",
    instruction=transaction_instruction,
    tools=[get_price,buy_stock, sell_stock, information_tool]
)

monitoring_agent = LlmAgent(
    name="monitoring_agent",
    model="gemini-2.0-flash",
    description="Assists the user with stock monitoring.",
    instruction=monitoring_instruction,
    tools=[get_price, update_watchlist, remove_from_watchlist, information_tool]
)

strategy_agent = LlmAgent(
    name="strategy_agent",
    model="gemini-2.0-flash",
    description="Gives investment advice to the user with the help of tools.",
    instruction=strategy_instruction,
    tools=[run_strategy_1, run_strategy_2]
)

root_agent = LlmAgent(
    name="trading_agent",
    model="gemini-2.0-flash",
    description="Assists the user with stock trading with the help of specialized sub-agents.",
    instruction=root_agent_instruction,
    sub_agents=[monitoring_agent, transactions_agent, strategy_agent],#, analysis_agent],
    before_model_callback=my_before_model_logic,
)
