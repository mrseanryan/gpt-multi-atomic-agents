from dataclasses import dataclass
from atomic_agents.agents.base_agent import (
    BaseIOSchema,
    BaseAgent,
    BaseAgentConfig,
)
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator
from pydantic import Field


from . import util_ai
from .config import Config


@dataclass
class AgentDescription:
    agent_name: str = Field(
        description="The name of the agent", examples=["Creature Creator"]
    )
    description: str = Field(
        description="The description of this agent, its purpose and capabilities."
    )
    topics: list[str] = Field(
        description="This agent ONLY generates if user mentioned one of these topics"
    )
    agent_parameter_names: list[str] = Field(
        description="A list of agent parameters that you can extract from the user's prompt."
    )  # Agent Parameters can be used by client to know what context to include in generation requests.


def _build_chat_agent_description(description: str) -> AgentDescription:
    return AgentDescription(
        agent_name="chat",
        description=description,
        topics=[],
        agent_parameter_names=["subjects"],
    )


ParamNameToValues = dict[str, list[str]]


class RecommendedAgent(BaseIOSchema):
    """
    This schema represents one agent that you recommend be used to handle the user's prompt.
    The recommendation includes the name of the agent, and a version of the user's prompt that has been rewritten to suit that agent.
    """

    agent_name: str = Field(description="The name of the agent")
    rewritten_user_prompt: str = Field(
        description="The user's prompt, rewritten to suit this agent"
    )
    agent_parameters: ParamNameToValues = Field(
        description="Agent Parameters that you extracted from the user's prompt"
    )


class AgentExecutionPlanSchema(BaseIOSchema):
    """
    This schema represents a generated plan to execute agents to fulfill the user's request. The chat message should be non-technical - do NOT mention agents.
    """

    chat_message: str = Field(
        description="The chat response to the user's message - a friendly non-technical message. Do NOT mention agents."
    )
    recommended_agents: list[RecommendedAgent] = Field(
        description="The ordered list of agents that you recommend should be used to handle the user's prompt. Only the most relevant agents should be recommended."
    )
    # TODO: could group the agents via list of ParallelAgentsGroup - this could also allow client to execute the agents in stages, allowing for HITL


class RouterAgentInputSchema(BaseIOSchema):
    """
    This schema represents the input to the Router agent.
    The schema contains the user's prompt and the list of available agents. Each agent has a special purpose. You need to recommend one or more agents to handle the users prompt.
    """

    user_prompt: str = Field(description="The chat message from the user", default="")
    agent_descriptions: list[AgentDescription] = Field(
        description="The list of available agents, describing their abilities and topics"
    )
    previous_plan: AgentExecutionPlanSchema | None = Field(
        description="The previously executed plan which the user wants you to modify",
        default=None,
    )


class RouterAgentOutputSchema(BaseIOSchema):
    """
    This schema represents the output of the Router agent.
    """

    execution_plan: AgentExecutionPlanSchema = Field(
        description="The generated plan to execute the agents"
    )


def _build_system_prompt_generator_custom() -> SystemPromptGenerator:
    return SystemPromptGenerator(
        background=[
            "You are a router bot that recommends the most suitable of the available AI agents to handle the user's prompt.",
        ],
        steps=[
            # TODO: revise/improve these steps
            "Check if there is a previous plan - if so, you need to generate a new merged plan",
            "For each agent, consider whether it needs to be run to fulfull the user's prompt",
            "Only select agents that are really relevant to the user's prompt",
            "If you find no suitable agent, then generate a polite message to explain to the user that you cannot handle this request",
            "For each selected agent, rewrite the user's prompt to suit that agent",
        ],
        output_instructions=[
            "Take the user prompt and match it to a sequence of one or more of the available agents. If no suitable agent is available, then generate a polite message to explain to the user that you cannot handle this request."
        ],
    )


def create_router_agent(config: Config) -> BaseAgent:
    """
    Create a Router agent which can recommend one or more agents to handle the user's prompt. For quality it rewrites the user prompt for each agent.
    - this approach prevents agents answering prompts that are not really for them
    """
    client, model, max_tokens = util_ai.create_client(_config=config)

    agent = BaseAgent(
        config=BaseAgentConfig(
            client=client,
            model=model,
            system_prompt_generator=_build_system_prompt_generator_custom(),
            input_schema=RouterAgentInputSchema,
            output_schema=RouterAgentOutputSchema,
            max_tokens=max_tokens,
        )
    )
    return agent


def build_input(
    user_prompt: str,
    agent_descriptions: list[AgentDescription],
    chat_agent_description: str,
    previous_plan: AgentExecutionPlanSchema | None = None,
) -> RouterAgentInputSchema:
    agent_descriptions.append(_build_chat_agent_description(chat_agent_description))

    return RouterAgentInputSchema(
        user_prompt=user_prompt,
        agent_descriptions=agent_descriptions,
        previous_plan=previous_plan,
    )
