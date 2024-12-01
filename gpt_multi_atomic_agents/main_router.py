import logging
import typing

from rich.console import Console

from cornsnake import util_time

from . import prompts_router
from .agent_definition import (
    AgentDefinitionBase,
)
from .config import Config
from . import util_print_agent

console = Console()

logger = logging.getLogger(__file__)


def generate_plan(
    agent_definitions: list[AgentDefinitionBase],
    chat_agent_description: str,
    _config: Config,
    user_prompt: str,
    previous_plan: prompts_router.AgentExecutionPlanSchema | None = None,
) -> prompts_router.AgentExecutionPlanSchema:
    console.log("Routing...")
    """
    Generate an agent execution plan to fulfill the user prompt, using the provided agents.
    - can be called again, with new user prompt, providing human-in-the-loop feedback.

    note: calling this router seperately from generation (agent execution) helps to reduce the *perceived* time taken to generate, since the user gets an (intermediate) response earlier.
    """

    start = util_time.start_timer()

    # TODO: optimizate router:
    # - possibly run it on smaller (and faster) LLM
    # - could allow for Classifier based router, but then cannot rewrite prompts
    router_agent = prompts_router.create_router_agent(config=_config)
    response = typing.cast(
        prompts_router.RouterAgentOutputSchema,
        router_agent.run(
            prompts_router.build_input(
                user_prompt=user_prompt,
                agents=agent_definitions,
                chat_agent_description=chat_agent_description,
                previous_plan=previous_plan,
            )
        ),
    )

    util_print_agent.print_router_assistant(response, _config=_config)
    time_taken = util_time.end_timer(start=start)
    console.log(f"  time taken: {util_time.describe_elapsed_seconds(time_taken)}")

    return response.execution_plan
