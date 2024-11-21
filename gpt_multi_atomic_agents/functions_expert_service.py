import logging
import typing

from atomic_agents.agents.base_agent import (
    BaseAgent,
    BaseAgentConfig,
)
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator

from rich.console import Console
from rich.text import Text

from . import util_ai, prompts_router, prompts_agent, config
from .agent_definition import AgentDefinition
from .blackboard import Blackboard
from .functions_dto import FunctionAgentOutputSchema, FunctionSpecSchema

console = Console()

logger = logging.getLogger("functions_expert")

def build_system_prompt_generator_custom(allowed_functions_to_generate: list[FunctionSpecSchema], topics: list[str]):
    allowed_functions_to_generate_names = [f.function_name for f in allowed_functions_to_generate]

    return SystemPromptGenerator(
        background=[
            "You are a helpful assistant that can only generate function calls using the provided definitions."
        ],
        steps=[
            # TODO: could break the prompt down into steps
            prompts_agent.build_agent_prompt(allowed_functions_to_generate_names, topics)
        ],
        output_instructions=["Your output should always be a set of zero or more generated functions, using only the allowed function definitions."],
    )

def _print_agent(agent: prompts_router.RecommendedAgent, max_prompt_out_len: int=100, prefix="") -> None:
    rewritten_user_prompt = agent.rewritten_user_prompt if config.IS_DEBUG else agent.rewritten_user_prompt[:max_prompt_out_len] + "..."
    console.print(Text(f" {prefix} - [{agent.agent_name}]", style="cyan"))
    console.print(Text(f"  <-- '{rewritten_user_prompt}'", style="blue"))

def _print_router_assistant(message: prompts_router.RouterAgentOutputSchema) -> None:
    console.print(f":robot: [bold cyan]Assistant [router]: {message.chat_message}[/bold cyan]")
    console.print(Text(f"  - recommended agents:", style="blue"))
    for agent in message.recommended_agents:
        _print_agent(agent, max_prompt_out_len=50)

def _print_assistant(message: FunctionAgentOutputSchema, agent_name="general"):
    console.print(f":robot: [bold green]Assistant [{agent_name}]: {message.chat_message}[/bold green]")
    console.print(Text(f"  New function calls:", style="yellow"))
    console.print(message.generated_function_calls)

def _create_agent(agent_definition: AgentDefinition) -> BaseAgent:
    client, model, max_tokens = util_ai.create_client()

    agent = BaseAgent(
        config=BaseAgentConfig(
            client=client,
            model=model,
            system_prompt_generator=build_system_prompt_generator_custom(agent_definition.initial_input.functions_allowed_to_generate, agent_definition.topics),
            input_schema=agent_definition.input_schema,
            output_schema=agent_definition.output_schema,
            max_tokens=max_tokens
        )
    )
    return agent

def run_chat_loop(agent_definitions: list[AgentDefinition], chat_agent_description: str, test_prompt: str|None = None) -> list:
    initial_message = FunctionAgentOutputSchema(
        chat_message="How can I help you?",
        generated_function_calls=[]
    )

    _print_assistant(initial_message)

    # for more emojis - see "poetry run python -m rich.emoji"
    if test_prompt:
        console.print(f":sunglasses: You: {test_prompt}")

    blackboard = Blackboard()
    while True:
        user_input = test_prompt if test_prompt else console.input(":sunglasses: You: ")
        if not user_input:
            break

        with console.status("[bold green]Processing...") as status:
            try:
                console.log(f"Routing...")
                router_agent = prompts_router.create_router_agent()
                response = typing.cast(prompts_router.RouterAgentOutputSchema, router_agent.run(prompts_router.build_input(user_prompt=user_input, agents=agent_definitions, chat_agent_description=chat_agent_description)) )
                recommended_agents = response.recommended_agents

                _print_router_assistant(response)

                # Loop thru all the recommended agents, sending each one a rewritten version of the user prompt
                for recommended_agent in recommended_agents:
                    try:
                        if recommended_agent.agent_name == "chat":
                            # TODO: add a Chat agent - but not really needed
                            continue

                        console.log(f":robot: Executing agent {recommended_agent.agent_name}...")
                        _print_agent(recommended_agent, prefix="EXECUTING: ")
                        matching_agent_definitions = list(filter(lambda a: a.agent_name == recommended_agent.agent_name, agent_definitions))
                        if not matching_agent_definitions:
                            raise RuntimeError(f"Could not match recommended agent {recommended_agent.agent_name}")
                        if len(matching_agent_definitions) > 1:
                            console.print(f":warning: Matched more than one agent to {recommended_agent.agent_name}")
                        agent_definition = matching_agent_definitions[0]
                        agent = _create_agent(agent_definition)

                        response = agent.run(agent_definition.build_input(recommended_agent.rewritten_user_prompt, blackboard))
                        _print_assistant(response, agent_definition.agent_name)
                        blackboard.add_generated_functions(response.generated_function_calls)
                    except Exception as e:
                        logger.exception(e)
            except Exception as e:
                logger.exception(e)

            console.log(":robot: (done)")

        if test_prompt:
            break
    return blackboard.previously_generated_functions

# to debug - see agent.system_prompt_generator.generate_prompt()
