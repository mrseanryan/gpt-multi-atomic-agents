from atomic_agents.agents.base_agent import (
    BaseIOSchema,
)
from pydantic import Field

class GraphQLAgentInputSchema(BaseIOSchema):
    """
    This schema represents the input to the agent.
    The schema contains previously generated mutation calls, and the list of allowed generated mutations.
    """
    user_input: str = Field(description="The chat message from the user", default="")
    mutations_allowed_to_generate: list[str] = Field(description="Definitions of the mutations that this agent can generate")
    previously_generated_mutations: list[str] = Field(description="Previously generated mutations in this chat (some are from other agents)", default_factory=lambda: list)

class GraphQLAgentOutputSchema(BaseIOSchema):
    """
    This schema represents the output of the agent.
    """
    chat_message: str = Field(description="The chat response to the user's message")
    generated_mutations: list[str] = Field(description="The set of new generated mutation calls")
