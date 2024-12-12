from atomic_agents.agents.base_agent import (
    BaseIOSchema,
)
from pydantic import Field

ParamNameToValues = dict[str, list[str]]


class GraphQLAgentInputSchema(BaseIOSchema):
    """
    This schema represents the input to the agent.
    The schema contains previously generated mutation calls, and the list of allowed generated mutations.
    """

    user_input: str = Field(description="The chat message from the user", default="")

    mutations_allowed_to_generate: list[str] = Field(
        description="Definitions of the GraphQL mutations that this agent can generate"
    )
    previously_generated_mutations: list[str] = Field(
        description="Previously generated GraphQL mutations in this chat (some are from other agents)",
        default_factory=lambda: list,
    )
    topics: list[str] = Field(
        description="This agent ONLY generates if user mentioned one of these topics"
    )
    agent_parameters: ParamNameToValues = Field(
        description="A dictionary of agent parameters there were extracted from the user's prompt.",
        default_factory=lambda: dict,
    )
    # TODO - add "If data is missing, then you need to generate allowed GraphQL queries."
    graphql_data: str = Field(
        description="The input GraphQL data from the client. You need to generate allowed GraphQL mutations that the client will use to update the data.",
        default="",
    )


class GraphQLAgentOutputSchema(BaseIOSchema):
    """
    This schema represents the output of the agent. The chat message should be non-technical - do NOT mention GraphQL.
    """

    chat_message: str = Field(
        description="The chat response to the user's message - a friendly non-technical message. Do NOT mention GraphQL."
    )
    generated_mutations: list[str] = Field(
        description="The set of new generated mutation calls to update the graphql_data. Only generate if neccessary (check if the graphql_data already has the data)."
    )
    # TODO Add generated_queries - generate queries if need more graphql_data
