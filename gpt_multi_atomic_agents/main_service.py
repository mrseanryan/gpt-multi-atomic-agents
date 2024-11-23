import logging
import typing

from atomic_agents.agents.base_agent import (
    BaseAgent,
    BaseAgentConfig,
)

from rich.console import Console

from . import util_ai, prompts_router
from .agent_definition import (
    AgentDefinitionBase,
    FunctionAgentDefinition,
)
from .blackboard import Blackboard
from .config import Config
from .functions_dto import FunctionAgentOutputSchema
from . import util_print_agent

console = Console()

logger = logging.getLogger("main_service")


def _create_agent(agent_definition: AgentDefinitionBase, _config: Config) -> BaseAgent:
    client, model, max_tokens = util_ai.create_client(_config=_config)
    system_prompt_builder = agent_definition.get_system_prompt_builder(_config=_config)

    agent = BaseAgent(
        config=BaseAgentConfig(
            client=client,
            model=model,
            system_prompt_generator=system_prompt_builder.build_system_prompt(),
            input_schema=agent_definition.input_schema,
            output_schema=agent_definition.output_schema,
            max_tokens=max_tokens,
        )
    )
    return agent


def run_chat_loop(
    agent_definitions: list[AgentDefinitionBase],
    chat_agent_description: str,
    _config: Config,
    given_user_prompt: str | None = None,
) -> list:
    if not agent_definitions:
        raise RuntimeError("Expected at least 1 Agent Definition")
    is_function_based = isinstance(agent_definitions[0], FunctionAgentDefinition)

    initial_message = FunctionAgentOutputSchema(
        chat_message="How can I help you?", generated_function_calls=[]
    )

    util_print_agent.print_assistant_functions(initial_message)

    # for more emojis - see "poetry run python -m rich.emoji"
    if given_user_prompt:
        console.print(f":sunglasses: You: {given_user_prompt}")

    blackboard = Blackboard()
    while True:
        user_prompt = (
            given_user_prompt
            if given_user_prompt
            else console.input(":sunglasses: You: ")
        )
        if not user_prompt:
            break

        with console.status("[bold green]Processing...") as _status:
            try:
                console.log("Routing...")
                router_agent = prompts_router.create_router_agent(config=_config)
                response = typing.cast(
                    prompts_router.RouterAgentOutputSchema,
                    router_agent.run(
                        prompts_router.build_input(
                            user_prompt=user_prompt,
                            agents=agent_definitions,
                            chat_agent_description=chat_agent_description,
                        )
                    ),
                )
                recommended_agents = response.recommended_agents

                util_print_agent.print_router_assistant(response, _config=_config)

                # Loop thru all the recommended agents, sending each one a rewritten version of the user prompt
                for recommended_agent in recommended_agents:
                    try:
                        if recommended_agent.agent_name == "chat":
                            # TODO: add a Chat agent - but not really needed
                            continue

                        console.log(
                            f":robot: Executing agent {recommended_agent.agent_name}..."
                        )
                        util_print_agent.print_agent(
                            recommended_agent, _config=_config, prefix="EXECUTING: "
                        )
                        matching_agent_definitions = list(
                            filter(
                                lambda a: a.agent_name == recommended_agent.agent_name,
                                agent_definitions,
                            )
                        )
                        if not matching_agent_definitions:
                            raise RuntimeError(
                                f"Could not match recommended agent {recommended_agent.agent_name}"
                            )
                        if len(matching_agent_definitions) > 1:
                            console.print(
                                f":warning: Matched more than one agent to {recommended_agent.agent_name}"
                            )
                        agent_definition = matching_agent_definitions[0]
                        agent = _create_agent(agent_definition, _config=_config)

                        response = agent.run(
                            agent_definition.build_input(
                                recommended_agent.rewritten_user_prompt,
                                blackboard=blackboard,
                                config=_config,
                            )
                        )
                        util_print_agent.print_assistant_output(
                            response, agent_definition
                        )

                        agent_definition.update_blackboard(
                            response=response, blackboard=blackboard
                        )
                    except Exception as e:
                        logger.exception(e)
            except Exception as e:
                logger.exception(e)

            console.log(":robot: (done)")

        if given_user_prompt:
            break
    return (
        blackboard.previously_generated_functions
        if is_function_based
        else blackboard.previously_generated_mutation_calls
    )


# to debug - see agent.system_prompt_generator.generate_prompt()
