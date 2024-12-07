from gpt_multi_atomic_agents.agent_definition import build_function_agent_definition
from . import functions


def build_creature_agent():
    agent_definition = build_function_agent_definition(
        agent_name=functions.creature_agent_name,
        description="Creates new creatures given the user prompt. Ensures that ALL creatures mentioned by the user are created.",
        accepted_functions=[
            functions.function_create_creature,
            functions.function_create_relationship,
        ],
        functions_allowed_to_generate=[functions.function_create_creature],
        topics=["creature"],
    )

    return agent_definition


def build_vegatation_agent():
    agent_definition = build_function_agent_definition(
        agent_name=functions.vegetation_agent_name,
        description="Creates new vegetation matching the user prompt. IMPORTANT: Ensures that ALL vegetation and plants mentioned by the user are created.",
        accepted_functions=[
            functions.function_create_vegetation,
            functions.function_create_relationship,
        ],
        functions_allowed_to_generate=[functions.function_create_vegetation],
        topics=["vegetation"],
    )

    return agent_definition


def build_relationship_agent():
    agent_definition = build_function_agent_definition(
        agent_name=functions.relationship_agent_name,
        description="Creates new relationships between creatures given the user prompt",
        accepted_functions=[
            functions.function_create_creature,
            functions.function_create_vegetation,
            functions.function_create_relationship,
        ],
        functions_allowed_to_generate=[functions.function_create_relationship],
        topics=["relationship"],
    )

    return agent_definition
