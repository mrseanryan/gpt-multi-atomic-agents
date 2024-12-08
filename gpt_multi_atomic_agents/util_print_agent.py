import typing

from atomic_agents.agents.base_agent import (
    BaseIOSchema,
)

from rich.console import Console
from rich.text import Text

from . import prompts_router, config
from .agent_definition import (
    AgentDefinitionBase,
    FunctionAgentDefinition,
    GraphQLAgentDefinition,
)
from .functions_dto import FunctionAgentOutputSchema
from .graphql_dto import GraphQLAgentOutputSchema

console = Console()


def print_agent(
    agent: prompts_router.RecommendedAgent,
    _config: config.Config,
    max_prompt_out_len: int = 200,
    prefix="",
) -> None:
    rewritten_user_prompt = agent.rewritten_user_prompt
    if not _config.is_debug and len(rewritten_user_prompt) > max_prompt_out_len:
        rewritten_user_prompt = agent.rewritten_user_prompt[:max_prompt_out_len] + "..."
    console.print(Text(f" {prefix} - [{agent.agent_name}]", style="cyan"))
    console.print(Text(f"  <-- '{rewritten_user_prompt}'", style="blue"))


def print_router_assistant(
    message: prompts_router.RouterAgentOutputSchema, _config: config.Config
) -> None:
    console.print(
        f":robot: [bold cyan]Assistant [router]: {message.execution_plan.chat_message}[/bold cyan]"
    )
    console.print(Text("  - recommended agents:", style="blue"))
    for agent in message.execution_plan.recommended_agents:
        print_agent(agent, _config=_config)


def print_assistant_message_only(chat_message: str, agent_name="general"):
    console.print(
        f":robot: [bold green]Assistant [{agent_name}]: {chat_message}[/bold green]"
    )


def _print_assistant_base(chat_message: str, output: typing.Any, agent_name="general"):
    print_assistant_message_only(chat_message=chat_message, agent_name=agent_name)
    console.print(Text("  New calls:", style="yellow"))
    console.print(output)


def print_assistant_message(message: str):
    initial_message = FunctionAgentOutputSchema(
        chat_message=message, generated_function_calls=[]
    )
    print_assistant_functions(message=initial_message)


def print_assistant_functions(message: FunctionAgentOutputSchema, agent_name="general"):
    return _print_assistant_base(
        message.chat_message, message.generated_function_calls, agent_name=agent_name
    )


def _print_assistant_graphql(message: GraphQLAgentOutputSchema, agent_name="general"):
    return _print_assistant_base(
        message.chat_message, message.generated_mutations, agent_name=agent_name
    )


def print_assistant_output(
    response: BaseIOSchema, agent_definition: AgentDefinitionBase
) -> None:
    if isinstance(agent_definition, FunctionAgentDefinition):
        return print_assistant_functions(response, agent_definition.agent_name)
    elif isinstance(agent_definition, GraphQLAgentDefinition):
        return _print_assistant_graphql(response, agent_definition.agent_name)
    else:
        raise RuntimeError("Not a recognised AgentDefinitionBase")


def print_user_prompt(user_prompt: str) -> None:
    console.print(f":sunglasses: You: {user_prompt}")
