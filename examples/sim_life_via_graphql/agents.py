import os

from cornsnake import util_file
from gpt_multi_atomic_agents.agent_definition import GraphQLAgentDefinition
from gpt_multi_atomic_agents.graphql_dto import (
    GraphQLAgentInputSchema,
    GraphQLAgentOutputSchema,
)


def _read_schema(filename: str) -> str:
    return util_file.read_text_from_file(
        os.path.join(util_file.get_this_script_dir(__file__), "schemas", filename)
    )


creatures_graphql = _read_schema("creature.graphql")
creature_mutations_graphql = _read_schema("creature.mutations.graphql")


def build_creature_agent():
    agent_definition = GraphQLAgentDefinition(
        agent_name="Creature Creator",
        description="Creates new creatures given the user prompt. Ensures that ALL creatures mentioned by the user are created, but ONLY if they are not already in graphql_data.",
        input_schema=GraphQLAgentInputSchema,
        initial_input=GraphQLAgentInputSchema(
            accepted_graphql_schemas=[creatures_graphql, creature_mutations_graphql],
            graphql_data="",
            mutations_allowed_to_generate=[creature_mutations_graphql],
            previously_generated_mutations=[],
            topics=["creature"],
        ),
        output_schema=GraphQLAgentOutputSchema,
    )

    return agent_definition


vegetation_mutations_graphql = _read_schema("vegetation.mutations.graphql")


def build_vegatation_agent():
    agent_definition = GraphQLAgentDefinition(
        agent_name="Vegetation Creator",
        description="Creates new vegetation matching the user prompt. IMPORTANT: Ensures that ALL vegetation and plants mentioned by the user are created.",
        input_schema=GraphQLAgentInputSchema,
        initial_input=GraphQLAgentInputSchema(
            accepted_graphql_schemas=[creatures_graphql, vegetation_mutations_graphql],
            graphql_data="",
            mutations_allowed_to_generate=[vegetation_mutations_graphql],
            previously_generated_mutations=[],
            topics=["vegetation"],
        ),
        output_schema=GraphQLAgentOutputSchema,
    )

    return agent_definition


relationship_mutations_graphql = _read_schema("relationship.mutations.graphql")


def build_relationship_agent():
    agent_definition = GraphQLAgentDefinition(
        agent_name="Relationship Creator",
        description="Creates new relationships between creatures given the user prompt",
        input_schema=GraphQLAgentInputSchema,
        initial_input=GraphQLAgentInputSchema(
            accepted_graphql_schemas=[
                creatures_graphql,
                creature_mutations_graphql,
                vegetation_mutations_graphql,
                relationship_mutations_graphql,
            ],
            graphql_data="",
            mutations_allowed_to_generate=[relationship_mutations_graphql],
            previously_generated_mutations=[],
            topics=["relationship"],
        ),
        output_schema=GraphQLAgentOutputSchema,
    )

    return agent_definition
