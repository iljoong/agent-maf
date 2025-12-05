import logging
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from agent_framework.azure import AzureOpenAIResponsesClient, AzureOpenAIChatClient
from agent_framework import (
    ChatAgent,
    HostedCodeInterpreterTool,
)

import os
from dotenv import load_dotenv
load_dotenv()

from .tools.weather_tool import get_current_weather
from .tools.stockprice_tool import (
    get_stock_price_range,
    get_stock_price_current,
    get_currency_rate_current,
)

system_instruction = """
You are a helpful assistant that helps the user with the help of some functions.
If you are using multiple tools to solve a user's task, make sure to communicate information learned from one tool to the next tool.
First, make a plan of how you will use the tools to solve the user's task and communicated that plan to the user with the first response. 
Then execute the plan making sure to communicate the required information between tools since tools only see the information passed to them;
They do not have access to the chat history.
If you think that tool use can be parallelized (e.g. to get weather data for multiple cities)
make sure to use the multi_tool_use.parallel function to execute.

You will use `get_stock_price_range` to get the stock price data for a given stock ticker within a specified date range.
You will use `code_interpreter` to run the analysis.

Don't make assumptions about what values to plug into functions. Ask for clarification if a user request is ambiguous.
If you don't know the answer, just say that you don't know, don't try to make up an answer.

Today is {datetime.now().strftime('%Y-%m-%d')}.
"""

agent = ChatAgent(
    name="Finance Agent",
    instructions=system_instruction,
    chat_client=AzureOpenAIChatClient(
        api_key=os.environ.get("AZURE_OPENAI_API_KEY", ""),
        end_point=os.environ.get("AZURE_OPENAI_ENDPOINT", ""),
        deployment_name="gpt-4.1-mini",
        #api_version="preview",
    ),
    tools=[get_current_weather, 
           get_stock_price_range, get_stock_price_current, get_currency_rate_current,
           HostedCodeInterpreterTool()]
)

def main():
    from agent_framework.devui import serve

    # Setup logging
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger(__name__)

    logger.info("Starting Agent")
    logger.info("Available at: http://localhost:8090")

    # Launch server with the agent
    serve(entities=[agent], port=8090, auto_open=True)

if __name__ == "__main__":
    main()