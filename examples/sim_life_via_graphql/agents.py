import os

from cornsnake import util_file
from gpt_multi_atomic_agents.agent_definition import build_graphql_agent_definition


def _read_schema(filename: str) -> str:
    return util_file.read_text_from_file(
        os.path.join(util_file.get_this_script_dir(__file__), "schemas", filename)
    )


creatures_graphql = _read_schema("creature.graphql")
creature_mutations_graphql = _read_schema("creature.mutations.graphql")


def build_creature_agent():
    agent_definition = build_graphql_agent_definition(
        agent_name="Creature Creator",
        description="Creates new creatures given the user prompt. Ensures that ALL creatures mentioned by the user are created, but ONLY if they are not already in graphql_data.",
        accepted_graphql_schemas=[creatures_graphql, creature_mutations_graphql],
        mutations_allowed_to_generate=[creature_mutations_graphql],
        topics=["creature", "summary"],
    )

    return agent_definition


vegetation_mutations_graphql = _read_schema("vegetation.mutations.graphql")


def build_vegatation_agent():
    agent_definition = build_graphql_agent_definition(
        agent_name="Vegetation Creator",
        description="Creates new vegetation matching the user prompt. IMPORTANT: Ensures that ALL vegetation and plants mentioned by the user are created.",
        accepted_graphql_schemas=[creatures_graphql, vegetation_mutations_graphql],
        mutations_allowed_to_generate=[vegetation_mutations_graphql],
        topics=["vegetation", "summary"],
    )

    return agent_definition


relationship_mutations_graphql = _read_schema("relationship.mutations.graphql")


def build_relationship_agent():
    agent_definition = build_graphql_agent_definition(
        agent_name="Relationship Creator",
        description="Creates new relationships between creatures given the user prompt",
        accepted_graphql_schemas=[
            creatures_graphql,
            creature_mutations_graphql,
            vegetation_mutations_graphql,
            relationship_mutations_graphql,
        ],
        mutations_allowed_to_generate=[relationship_mutations_graphql],
        topics=["relationship", "summary"],
    )

    return agent_definition
