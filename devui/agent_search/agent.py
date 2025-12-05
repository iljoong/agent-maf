import logging
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

from agent_framework.azure import AzureOpenAIResponsesClient, AzureOpenAIChatClient
from agent_framework import (
    ChatAgent,
    HostedWebSearchTool,
)

import os
from dotenv import load_dotenv
load_dotenv()

agent = ChatAgent(
    name="Web Search Agent",
    instructions="You are a helpful assistant with web search capabilities",
    chat_client=AzureOpenAIResponsesClient(
        api_key=os.environ.get("AZURE_OPENAI_API_KEY", ""),
        end_point=os.environ.get("AZURE_OPENAI_ENDPOINT", ""),
        deployment_name="gpt-4.1-mini",
        #api_version="preview",
    ),
    tools=[
        HostedWebSearchTool(
            additional_properties={
                "user_location": {
                    "city": "Seoul",
                    "country": "KR"
                }
            }
        )
    ]
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