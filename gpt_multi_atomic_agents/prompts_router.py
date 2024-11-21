from dataclasses import dataclass
from atomic_agents.agents.base_agent import (
    BaseIOSchema,
    BaseAgent,
    BaseAgentConfig,
)
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from pydantic import Field

from . import util_ai
from .agent_definition import AgentDefinition

@dataclass
class AgentDescription:
    agent_name: str = Field(description="The name of the agent")
    description: str = Field(description="The description of this agent, its purpose and capabilities.")
    topics: str = Field(description="This agent ONLY generates if user mentioned one of these topics")

def _build_chat_agent(description: str) -> AgentDescription:
    return AgentDescription(agent_name= "chat", description=description, topics=[])

class RouterAgentInputSchema(BaseIOSchema):
    """
    This schema represents the input to the Router agent.
    The schema contains the user's prompt and the list of available agents. Each agent has a special purpose. You need to recommend one or more agents to handle the users prompt.
    """
    user_prompt: str = Field(description="The chat message from the user", default="")
    agent_descriptions: list[AgentDescription] = Field(description="The list of available agents, describing their abilities and topics")

class RecommendedAgent(BaseIOSchema):
    """
    This schema represents one agent that you recommend be used to handle the user's prompt.
    The recommendation includes the name of the agent, and a version of the user's prompt that has been rewritten to suit that agent.
    """
    agent_name: str = Field(description="The name of the agent")
    rewritten_user_prompt: str = Field(description="The user's prompt, rewritten to suit this agent")


class RouterAgentOutputSchema(BaseIOSchema):
    """
    This schema represents the output of the Router agent.
    """
    chat_message: str = Field(description="The chat response to the user's message")
    recommended_agents: list[RecommendedAgent] = Field(description="The list of agents that you recommend should be used to handle the user's prompt. Only the most relevant agents should be recommended.")

def _serialize_agent(agent: AgentDefinition) -> AgentDescription:
    topics = ", ".join(agent.topics)
    return AgentDescription(agent_name=agent.agent_name, description=agent.description, topics=topics)

def _serialize_agents(agents: list[AgentDefinition]) -> list[AgentDescription]:
    all_agents = agents
    return [_serialize_agent(a) for a in all_agents ]

def _build_system_prompt_generator_custom() -> SystemPromptGenerator:
    return SystemPromptGenerator(
        background=[
            "You are a router bot that recommends the most suitable of the available AI agents to handle the user's prompt.",
        ],
        steps=[

            # TODO: revise/improve these steps
            "For each agent, consider whether it needs to be run to fulfull the user's prompt",
            "Only select agents that are really relevant to the user's prompt",
            "If you find no suitable agent, then default to the 'chat' agent",
            "For each selected agent, rewrite the user's prompt to suit that agent",
        ],
        output_instructions=["Take the user prompt and match it to a sequence of one or more of the available agents. If no suitable agent is available, use the 'chat' agent."],
    )


def create_router_agent() -> BaseAgent:
    """
    Create a Router agent which can recommend one or more agents to handle the user's prompt. For quality it rewrites the user prompt for each agent.
    - this approach prevents agents answering prompts that are not really for them
    """
    client, model, max_tokens = util_ai.create_client()

    agent = BaseAgent(
        config=BaseAgentConfig(
            client=client,
            model=model,
            system_prompt_generator=_build_system_prompt_generator_custom(),
            input_schema=RouterAgentInputSchema,
            output_schema=RouterAgentOutputSchema,
            max_tokens=max_tokens
        )
    )
    return agent

def build_input(user_prompt: str, agents: list[AgentDefinition], chat_agent_description:str) -> RouterAgentInputSchema:
    active_agents = agents + [_build_chat_agent(chat_agent_description)]
    return RouterAgentInputSchema(user_prompt=user_prompt, agent_descriptions=_serialize_agents(active_agents))
