import logging
import time
from fastapi import FastAPI, Request
from pydantic import Field

from .blackboard import FunctionCallBlackboard
from .rest_api_examples import (
    FunctionAgentDefinitionMinimal,
    creature_agent_name,
    example_creeature_creator_agent,
)

from .config import load_config, Config
from .util_pydantic import CustomBaseModel

from . import prompts_router
from .agent_definition import FunctionAgentDefinition, build_function_agent_definition

from . import main_router
from . import main_generator

logger = logging.getLogger(__file__)

app = FastAPI()


def _load_config_from_ini() -> Config:
    return load_config(path_to_ini="config.ini")


class AsyncIteratorWrapper:
    """The following is a utility class that transforms a
    regular iterable to an asynchronous one.

    link: https://www.python.org/dev/peps/pep-0492/#example-2
    """

    def __init__(self, obj):
        self._it = iter(obj)

    def __aiter__(self):
        return self

    async def __anext__(self):
        try:
            value = next(self._it)
        except StopIteration:
            raise StopAsyncIteration
        return value


@app.middleware("http")
async def add_request_response_logging(request: Request, call_next):
    start_time = time.perf_counter()

    config = _load_config_from_ini()
    if config.is_debug:
        print("REQUEST HEADERS", request.headers)
        request_body = await request.body()
        print("REQUEST BODY", request_body)

    response = await call_next(request)
    process_time = time.perf_counter() - start_time

    if config.is_debug:
        resp_body = [section async for section in response.__dict__["body_iterator"]]
        response.__setattr__("body_iterator", AsyncIteratorWrapper(resp_body))
        print("RESPONSE BODY", str(resp_body))

    response.headers["X-Process-Time"] = str(process_time)
    return response


class GeneratePlanRequest(CustomBaseModel):
    agent_descriptions: list[prompts_router.AgentDescription] = Field(
        description="The descriptions of the available Agents. The response will contain the most suitable agents to execute in order.",
        examples=[
            [
                {
                    "agent_name": creature_agent_name,
                    "description": "Creates new creatures given the user prompt. Ensures that ALL creatures mentioned by the user are created.",
                    "topics": ["creature"],
                    "agent_parameter_names": ["creature_name"],
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
                "chat_message": "Certainly! I'll help you add a sheep that eats grass to your ecosystem.",
                "recommended_agents": [
                    {
                        "agent_name": creature_agent_name,
                        "rewritten_user_prompt": "Create a new creature: sheep. The sheep should have the ability to eat grass.",
                        "agent_parameters": {"creature_name": ["sheep"]},
                    }
                ],
            }
        ],
        default=None,
    )


class FunctionCallGenerateRequest(CustomBaseModel):
    agent_definitions: list[FunctionAgentDefinitionMinimal] = Field(
        description="The defintions of the Agents to execute, in order.",
        examples=[[example_creeature_creator_agent]],
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
                "chat_message": "Certainly! I'll help you add a sheep that eats grass to your ecosystem.",
                "recommended_agents": [
                    {
                        "agent_name": creature_agent_name,
                        "rewritten_user_prompt": "Create a new creature: sheep. The sheep should have the ability to eat grass.",
                        "agent_parameters": {"creature_name": ["sheep"]},
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
        _config=_load_config_from_ini(),
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

    if request.blackboard:
        request.blackboard.reset_newly_generated()  # in case client did not clear out

    return main_generator.generate_with_blackboard(
        agent_definitions=agent_definitions,
        chat_agent_description=request.chat_agent_description,
        _config=_load_config_from_ini(),
        user_prompt=request.user_prompt,
        blackboard=request.blackboard,
        execution_plan=request.execution_plan,
    )


# TODO (someone): Later add generate_graphql()
