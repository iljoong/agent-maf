import os
from collections.abc import Awaitable, Callable
from typing import Annotated

from agent_framework import (
    ChatAgent,
    ChatMessage,
    WorkflowBuilder,
    WorkflowContext,
    executor,
    AgentExecutor,
    AgentRunUpdateEvent,
    AgentExecutorResponse,
    AgentExecutorRequest,
    AgentRunResponse,
    Role,
    ToolMode,
    HostedWebSearchTool,
)
from agent_framework.azure import AzureOpenAIResponsesClient

chat_client=AzureOpenAIResponsesClient(
    api_key=os.environ.get("AZURE_OPENAI_API_KEY", ""),
    end_point=os.environ.get("AZURE_OPENAI_ENDPOINT", ""),
    deployment_name="gpt-4.1-mini",
    api_version="preview",
)

from .prompt_template import intent_template, plan_template, report_template

from pydantic import BaseModel
from enum import Enum

class ResearchTopic(BaseModel):
    topic: str
    steps: list[str]

class ResearchTopics(BaseModel):
    topics: list[ResearchTopic]
    user_message: str

# Itent Enum
class IntentEnum(str, Enum):
    CHAT = "chat"
    RESEARCH = "research"

class IntentResponse(BaseModel):
    intent: IntentEnum
    user_message: str

intent_executor = AgentExecutor(
    chat_client.create_agent(
        name="intent_agent",
        instructions=intent_template,
        response_format=IntentResponse,
    ),
    id="intent_agent",
)

chat_exectutor = AgentExecutor(
    chat_client.create_agent(
        name="chat_agent",
        instructions="You're an intelligent assistant. Answer user's question or ask.",
    ),
    id="chat_exectutor",
)

@executor(id="to_chat_executor")
async def to_chat_executor(
    response: AgentExecutorResponse, ctx: WorkflowContext[AgentExecutorRequest]
) -> None:
    
    # Bridge executor. Converts a structured DetectionResult into a ChatMessage and forwards it as a new request.
    intent: IntentResponse = IntentResponse.model_validate_json(response.agent_run_response.text)
    user_msg = ChatMessage(Role.USER, text=intent.user_message)
    await ctx.send_message(AgentExecutorRequest(messages=[user_msg], should_respond=True))

@executor(id="to_plan_executor")
async def to_plan_executor(
    response: AgentExecutorResponse, ctx: WorkflowContext[AgentExecutorRequest]
) -> None:

    # Bridge executor. Converts a structured DetectionResult into a ChatMessage and forwards it as a new request.
    intent: IntentResponse = IntentResponse.model_validate_json(response.agent_run_response.text)
    user_msg = ChatMessage(Role.USER, text=intent.user_message)

    await ctx.send_message(AgentExecutorRequest(messages=[user_msg], should_respond=True))

plan_exectutor = AgentExecutor(
    chat_client.create_agent(
        name="plan_agent",
        instructions=plan_template,
        response_format=ResearchTopics,
    ),
    id="plan_exectutor",
)

@executor(id="to_report_executor")
async def to_report_executor(
    response: AgentExecutorResponse, ctx: WorkflowContext[AgentExecutorRequest]
) -> None:

    # Bridge executor. Converts a structured DetectionResult into a ChatMessage and forwards it as a new request.
    research_topics: ResearchTopics = ResearchTopics.model_validate_json(response.agent_run_response.text)

    report_prompt = report_template.format(
        topics="\n".join(
            f"Topics and steps: {topic.topic}\n" + "\n".join(f"- {step}" for step in topic.steps)
            for topic in research_topics.topics
        ),
        query=research_topics.user_message,
    ) 

    user_msg = ChatMessage(Role.USER, text=report_prompt)

    await ctx.send_message(AgentExecutorRequest(messages=[user_msg], should_respond=True))

report_exectutor = AgentExecutor(
    chat_client.create_agent(
        name="report_agent",
        instructions=("Based on the research plan, write a detailed report that directly answers the user's request."
        "Use tools to search the web and gather relevant information for topics & steps in <research_topics> tag."),
        tool_choice=ToolMode.REQUIRED_ANY,
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
    ),
    id="report_exectutor",
)

from typing import Any

def get_intent(expected_intent:IntentEnum):
    """create a condition callable that routes based on intent"""

    def condition(message: Any) -> bool:
        if not isinstance(message, AgentExecutorResponse):
            return True
        
        try:
            intent = IntentResponse.model_validate_json(message.agent_run_response.text)
            
            return intent.intent == expected_intent
        except Exception:
            return False

    return condition

workflow = (
    WorkflowBuilder(
        name="Research Workflow",
        description="Multi-agent research workflow with conditional routing based on user intent."
    )
    .set_start_executor(intent_executor)
    .add_edge(intent_executor, to_chat_executor, condition=get_intent(IntentEnum.CHAT))
    .add_edge(to_chat_executor, chat_exectutor)
    .add_edge(intent_executor, to_plan_executor, condition=get_intent(IntentEnum.RESEARCH))
    .add_edge(to_plan_executor, plan_exectutor)
    .add_edge(plan_exectutor, to_report_executor)
    .add_edge(to_report_executor, report_exectutor)
    .build())

def main():
    """Launch the branching workflow in DevUI."""
    import logging

    from agent_framework.devui import serve

    logging.basicConfig(level=logging.INFO, format="%(message)s")
    logger = logging.getLogger(__name__)

    logger.info("Starting Agent Workflow")
    logger.info("Available at: http://localhost:8090")
    logger.info("\nThis workflow demonstrates:")

    serve(entities=[workflow], port=8090, auto_open=True)


if __name__ == "__main__":
    main()