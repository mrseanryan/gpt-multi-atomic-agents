from pydantic import Field
from gpt_multi_atomic_agents.util_pydantic import CustomBaseModel
from .functions_dto import (
    FunctionCallSchema,
    FunctionSpecSchema,
    ParameterSpec,
    ParameterType,
    ParamNameToValues,
)

creature_agent_name = "Creature Creator"


class FunctionAgentDefinitionMinimal(CustomBaseModel):
    agent_name: str = Field(
        description="The name of the agent", examples=[creature_agent_name]
    )
    description: str = Field(
        description="The description of this agent, its purpose and capabilities."
    )
    accepted_functions: list[FunctionSpecSchema] = Field(
        description="The set of 'input' function calls that this agent understands. Each agent should understand its own output, but can also understand a subset of the output of other agents. This allows the agents to collaborate."
    )
    functions_allowed_to_generate: list[FunctionSpecSchema] = Field(
        description="The set of 'output' function calls that this agent generates."
    )
    topics: list[str] = Field(
        description="This agent ONLY generates if user mentioned one of these topics"
    )
    agent_parameters: ParamNameToValues = Field(
        description="A list of agent parameters to extract from the user prompt",
        default_factory=dict,  # TODO should this be 'lambda: dict' ? but rest-api does not like it.
    )  # To help with context retrieval by client after it receives the ExecutionPlan OR could help Agent to know what is user talking about


# Build examples programatically = less error prone
creature_icons = ["sheep-icon", "wolf-icon", "grass-icon", "human-icon", "other-icon"]
terrain_types = ["mountain", "marsh", "prairie", "coast", "water"]

function_create_creature = FunctionSpecSchema(
    function_name="AddCreature",
    description="Adds a new creature to the world (not vegetation)",
    parameters=[
        ParameterSpec(name="creature_name", type=ParameterType.string),
        ParameterSpec(
            name="allowed_terrain",
            type=ParameterType.string,
            allowed_values=terrain_types,
        ),
        ParameterSpec(name="age", type=ParameterType.int),
        ParameterSpec(
            name="icon_name", type=ParameterType.string, allowed_values=creature_icons
        ),
    ],
)

example_creeature_creator_agent = FunctionAgentDefinitionMinimal(
    agent_name=creature_agent_name,
    description="Creates new creatures given the user prompt. Ensures that ALL creatures mentioned by the user are created.",
    accepted_functions=[function_create_creature],
    functions_allowed_to_generate=[function_create_creature],
    topics=["creature", "summary"],
)

example_create_creature_call__wolf = FunctionCallSchema(
    agent_name=creature_agent_name,
    function_name=function_create_creature.function_name,
    parameters={
        "creature_name": "wolf",
        "allowed_terrain": "mountain",
        "age": "5",
        "icon_name": "wolf-icon",
    },
)
