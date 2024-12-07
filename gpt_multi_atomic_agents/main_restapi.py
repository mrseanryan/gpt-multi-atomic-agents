from fastapi import FastAPI
from pydantic import Field

from .blackboard import FunctionCallBlackboard
from .functions_dto import FunctionSpecSchema, ParameterSpec, ParameterType

from .config import load_config
from .util_pydantic import CustomBaseModel

from . import prompts_router
from .agent_definition import FunctionAgentDefinition, build_function_agent_definition

from . import main_router
from . import main_generator

app = FastAPI()
creature_agent_name = "Creature Creator"


class GeneratePlanRequest(CustomBaseModel):
    agent_descriptions: list[prompts_router.AgentDescription] = Field(
        description="The descriptions of the available Agents. The response will contain the most suitable agents to execute in order.",
        examples=[
            [
                {
                    "agent_name": creature_agent_name,
                    "description": "Creates new creatures given the user prompt. Ensures that ALL creatures mentioned by the user are created.",
                    "topics": ["creature"],
                }
            ]
        ],
    )
    chat_agent_description: str = Field(
        description="Describes the 'fallback' chat agent: if no suitable agents are recommended, this chat agent will be recommended, if the user's prompt is supported. The description should include the purpose and domain of this chat system.",
        examples=["Handles users questions about an ecosystem game like Sim Life"],
    )
    user_prompt: str = Field(
        description="The input from the user",
        examples=["Add a goat instead of a sheep"],
    )
    previous_plan: prompts_router.AgentExecutionPlanSchema | None = Field(
        description="Optionally also send a previously generated plan, so the AI can generate a new plan taking into account the user's feedback (in user_prompt).",
        examples=[
            {
                "chat_message": "Certainly! I'll help you add a sheep that eats grass to your ecosystem. I'll use the Creature Creator agent to create this new creature for you.",
                "recommended_agents": [
                    {
                        "agent_name": creature_agent_name,
                        "rewritten_user_prompt": "Create a new creature: sheep. The sheep should have the ability to eat grass.",
                    }
                ],
            }
        ],
        default=None,
    )


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


# Build examples programatically = less error prone
creature_icons = ["sheep-icon", "wolf-icon", "grass-icon", "human-icon", "other-icon"]
terrain_types = ["mountain", "marsh", "prairie", "coast", "water"]

function_create_creature = FunctionSpecSchema(
    agent_name=creature_agent_name,
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

accepted_functions = [function_create_creature]


class FunctionCallGenerateRequest(CustomBaseModel):
    agent_definitions: list[FunctionAgentDefinitionMinimal] = Field(
        description="The defintions of the Agents to execute, in order.",
        examples=[
            [
                {
                    "agent_name": creature_agent_name,
                    "description": "Creates new creatures given the user prompt. Ensures that ALL creatures mentioned by the user are created.",
                    "accepted_functions": accepted_functions,
                    "functions_allowed_to_generate": accepted_functions,
                    "topics": ["creature"],
                }
            ]
        ],
    )
    chat_agent_description: str = Field(
        description="Describe the purpose and domain of this chat system.",
        examples=["Handles users questions about an ecosystem game like Sim Life"],
    )
    user_prompt: str = Field(
        description="The input from the user", examples=["Add a sheep that eats grass"]
    )
    blackboard: FunctionCallBlackboard | None = Field(
        description="Optionally include the previous Blackboard state, to have a conversation (avoids stateless server). This contains previous state and new data (which the user has updated either by executing its implementation of Function Calls).",
        default=None,
    )
    execution_plan: prompts_router.AgentExecutionPlanSchema | None = Field(
        description="Optionally also include a previously generated plan, to reduce latency. If no plan is included, then generate will also internally call generate_plan.",
        examples=[
            {
                "chat_message": "Certainly! I'll help you add a sheep that eats grass to your ecosystem. I'll use the Creature Creator agent to create this new creature for you.",
                "recommended_agents": [
                    {
                        "agent_name": creature_agent_name,
                        "rewritten_user_prompt": "Create a new creature: sheep. The sheep should have the ability to eat grass.",
                    }
                ],
            }
        ],
        default=None,
    )


@app.post("/generate_plan")
async def generate_plan(
    request: GeneratePlanRequest,
) -> prompts_router.AgentExecutionPlanSchema:
    return main_router.generate_plan_via_descriptions(
        agent_descriptions=request.agent_descriptions,
        chat_agent_description=request.chat_agent_description,
        _config=load_config(path_to_ini="config.ini"),
        user_prompt=request.user_prompt,
        previous_plan=request.previous_plan,
    )


def _build_agent_definition_from_minimal(
    minimal_agent: FunctionAgentDefinitionMinimal,
) -> FunctionAgentDefinition:
    return build_function_agent_definition(
        agent_name=minimal_agent.agent_name,
        description=minimal_agent.description,
        accepted_functions=minimal_agent.accepted_functions,
        functions_allowed_to_generate=minimal_agent.functions_allowed_to_generate,
        topics=minimal_agent.topics,
    )


@app.post("/generate_function_calls")
def generate_function_calls(
    request: FunctionCallGenerateRequest,
) -> FunctionCallBlackboard:
    agent_definitions = [
        _build_agent_definition_from_minimal(a) for a in request.agent_definitions
    ]

    request.blackboard.reset_newly_generated()  # in case client did not clear out

    return main_generator.generate_with_blackboard(
        agent_definitions=agent_definitions,
        chat_agent_description=request.chat_agent_description,
        _config=load_config(path_to_ini="config.ini"),
        user_prompt=request.user_prompt,
        blackboard=request.blackboard,
        execution_plan=request.execution_plan,
    )


# TODO (someone): Later add generate_graphql()
