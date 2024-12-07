from gpt_multi_atomic_agents.functions_dto import (
    FunctionSpecSchema,
    ParameterType,
    ParameterSpec,
)

creature_agent_name = "Creature Creator"
vegetation_agent_name = "Vegetation Creator"
relationship_agent_name = "Relationship Creator"

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

function_create_vegetation = FunctionSpecSchema(
    function_name="AddVegetation",
    description="Adds new vegetation to the world",
    parameters=[
        ParameterSpec(name="vegetation_name", type=ParameterType.string),
        ParameterSpec(
            name="icon_name",
            type=ParameterType.string,
            allowed_values=creature_icons,
        ),
        ParameterSpec(
            name="allowed_terrain",
            type=ParameterType.string,
            allowed_values=terrain_types,
        ),
    ],
)

function_create_relationship = FunctionSpecSchema(
    function_name="AddCreatureRelationship",
    description="Adds a new relationship between two creatures",
    parameters=[
        ParameterSpec(name="from_name", type=ParameterType.string),
        ParameterSpec(name="to_name", type=ParameterType.string),
        ParameterSpec(
            name="relationship_name",
            type=ParameterType.string,
            allowed_values=["eats", "buys", "feeds", "sells"],
        ),
    ],
)
