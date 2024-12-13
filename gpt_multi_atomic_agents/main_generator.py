import logging
import typing

from atomic_agents.agents.base_agent import (
    BaseAgent,
    BaseAgentConfig,
    BaseIOSchema,
)
from cornsnake import util_time, util_wait
from rich.console import Console

from gpt_multi_atomic_agents.graphql_dto import GraphQLAgentOutputSchema

from .functions_dto import FunctionAgentOutputSchema
from .util_output import print_warning

from .blackboard_serde import load_blackboard_from_file

from .prompts_router import AgentExecutionPlanSchema

from . import main_router

from . import util_ai
from .agent_definition import (
    AgentDefinitionBase,
    FunctionAgentDefinition,
)
from .blackboard import (
    Blackboard,
    FunctionCallBlackboard,
    GraphQLBlackboard,
    Message,
    MessageRole,
)
from .blackboard_accessor import (
    BlackboardAccessor,
    FunctionCallBlackboardAccessor,
    GraphQLBlackboardAccessor,
)
from .config import Config
from .repl_commands import CommandAction, check_user_prompt, print_help
from . import util_print_agent

console = Console()

logger = logging.getLogger(__file__)


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


def _check_blackboard(
    blackboard: Blackboard, agent_definitions: list[AgentDefinitionBase]
) -> None:
    is_function_based = isinstance(agent_definitions[0], FunctionAgentDefinition)
    if blackboard:
        if is_function_based:
            if not (typing.cast(FunctionCallBlackboard, blackboard)):
                raise RuntimeError("Expected blackboard to be a FunctionCallBlackboard")
        elif not (typing.cast(GraphQLBlackboard, blackboard)):
            raise RuntimeError("Expected blackboard to be a GraphQLBlackboard")


def _create_blackboard_accessor(
    agent_definitions: list[AgentDefinitionBase],
) -> BlackboardAccessor:
    if not agent_definitions:
        raise RuntimeError("Expected at least 1 Agent Definition")
    is_function_based = isinstance(agent_definitions[0], FunctionAgentDefinition)
    blackboard = (
        FunctionCallBlackboardAccessor(_blackboard=FunctionCallBlackboard())
        if is_function_based
        else GraphQLBlackboardAccessor(_blackboard=GraphQLBlackboard())
    )
    return blackboard


def _create_blackboard_accessor_from_blackboard(
    blackboard: Blackboard,
) -> BlackboardAccessor:
    if isinstance(blackboard, FunctionCallBlackboard):
        return FunctionCallBlackboardAccessor(_blackboard=blackboard)
    elif isinstance(blackboard, GraphQLBlackboard):
        return GraphQLBlackboardAccessor(_blackboard=blackboard)

    raise RuntimeError("Not a recognised kind of Blackboard")


def generate(
    agent_definitions: list[AgentDefinitionBase],
    chat_agent_description: str,
    _config: Config,
    user_prompt: str,
    blackboard: (
        BlackboardAccessor | None
    ) = None,  # If used as a web service, then would also accept previous state + new data (which the user has updated either by executing its implementation of Function Calls OR by updating via GraphQL mutations).
    execution_plan: AgentExecutionPlanSchema | None = None,
) -> BlackboardAccessor:
    blackboard = generate_with_blackboard(
        agent_definitions=agent_definitions,
        chat_agent_description=chat_agent_description,
        _config=_config,
        user_prompt=user_prompt,
        blackboard=blackboard._blackboard,
        execution_plan=execution_plan,
    )
    return _create_blackboard_accessor_from_blackboard(blackboard=blackboard)


def _create_blackboard(
    agent_definitions: list[AgentDefinitionBase],
) -> BlackboardAccessor:
    if not agent_definitions:
        raise RuntimeError("Expected at least 1 Agent Definition")
    is_function_based = isinstance(agent_definitions[0], FunctionAgentDefinition)
    blackboard = FunctionCallBlackboard() if is_function_based else GraphQLBlackboard()
    return blackboard


def _fix_agent_name(
    response: BaseIOSchema, agent_definition: AgentDefinitionBase
) -> None:
    """Sometimes generate() hallucincates a new Agent Name (but planning does not!). We can easily post-fix it here."""
    if isinstance(response, FunctionAgentOutputSchema):
        did_warn = False
        for fun in response.generated_function_calls:
            if fun.agent_name != agent_definition.agent_name:
                if not did_warn:
                    print_warning(
                        message=f"LLM reponse has incorrect agent name '{fun.agent_name}' - fixing it to be '{agent_definition.agent_name}'"
                    )
                    did_warn = True
                fun.agent_name = agent_definition.agent_name
    elif isinstance(response, GraphQLAgentOutputSchema):
        pass  # no agent name in response
    else:
        raise RuntimeError("Not a recognised agent response")


def generate_with_blackboard(
    agent_definitions: list[AgentDefinitionBase],
    chat_agent_description: str,
    _config: Config,
    user_prompt: str,
    blackboard: (
        Blackboard | None
    ) = None,  # If used as a web service, then would also accept previous state + new data (which the user has updated either by executing its implementation of Function Calls OR by updating via GraphQL mutations).
    execution_plan: AgentExecutionPlanSchema | None = None,
) -> Blackboard:
    """
    Use the provided agents to fulfill the user's prompt.
    - if an execution plan is provided, that is used to decide which agents to execute.
       - else the router is used to generate an execution plan
    """

    start = util_time.start_timer()

    if blackboard:
        _check_blackboard(blackboard=blackboard, agent_definitions=agent_definitions)
    else:
        blackboard = _create_blackboard(agent_definitions)

    blackboard.add_previous_mesage(Message(role=MessageRole.user, message=user_prompt))

    with console.status("[bold green]Processing...") as _status:
        try:
            if not execution_plan:
                execution_plan = main_router.generate_plan(
                    agent_definitions=agent_definitions,
                    chat_agent_description=chat_agent_description,
                    _config=_config,
                    user_prompt=user_prompt,
                )
                blackboard.add_mesage(
                    Message(
                        role=MessageRole.assistant, message=execution_plan.chat_message
                    )
                )
                util_print_agent.print_assistant_message(execution_plan.chat_message)
                util_wait.wait_seconds(_config.delay_between_calls_in_seconds)

            # Loop thru all the recommended agents, sending each one a rewritten version of the user prompt
            for i, recommended_agent in enumerate(execution_plan.recommended_agents):
                try:
                    if recommended_agent.agent_name == "chat":
                        # TODO: add option to redirect to some Chat agent
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
                        print_warning(
                            f"Matched more than one agent to {recommended_agent.agent_name}"
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
                    _fix_agent_name(response, agent_definition)
                    util_print_agent.print_assistant_output(response, agent_definition)

                    agent_definition.update_blackboard(
                        response=response, blackboard=blackboard
                    )
                    is_last = i == len(execution_plan.recommended_agents) - 1
                    if not is_last:
                        util_wait.wait_seconds(_config.delay_between_calls_in_seconds)
                except Exception as e:
                    logger.exception(e)
        except Exception as e:
            logger.exception(e)

        console.log(":robot: (done)")
        time_taken = util_time.end_timer(start=start)
        console.log(f"  time taken: {util_time.describe_elapsed_seconds(time_taken)}")
    return blackboard


def run_chat_loop(
    agent_definitions: list[AgentDefinitionBase],
    chat_agent_description: str,
    _config: Config,
    given_user_prompt: str | None = None,
    blackboard: (
        BlackboardAccessor | None
    ) = None,  # If used as a web service, then would also accept previous state + new data (which the user has updated either by executing its implementation of Function Calls OR by updating via GraphQL mutations).
) -> BlackboardAccessor:
    """
    Use the provided agents to fulfill the user's prompt.
    - if an execution plan is provided, that is used to decide which agents to execute.
       - else the router is used to generate an execution plan
    - if no given user prompt is provided, then the user is prompted via keyboard input in a REPL loop.
    """

    if not blackboard:
        blackboard = _create_blackboard_accessor(agent_definitions)

    print_help()

    initial_assistant_message = "How can I help you?"
    util_print_agent.print_assistant_message_only(
        chat_message=initial_assistant_message
    )

    blackboard._blackboard.add_mesage(
        Message(role=MessageRole.assistant, message=initial_assistant_message)
    )

    # for more emojis - see "poetry run python -m rich.emoji"
    if given_user_prompt:
        util_print_agent.print_user_prompt(given_user_prompt)

    while True:
        user_prompt = (
            given_user_prompt
            if given_user_prompt
            else console.input(":sunglasses: You: ")
        )
        action = check_user_prompt(
            user_prompt=user_prompt, blackboard=blackboard._blackboard, config=_config
        )
        match action:
            case CommandAction.quit:
                util_print_agent.print_assistant_message_only(chat_message="Good bye!")
                break
            case CommandAction.handled_already:
                continue
            case CommandAction.load_blackboard:
                new_blackboard = load_blackboard_from_file(
                    config=_config, existing_blackboard=blackboard._blackboard
                )
                if new_blackboard:
                    blackboard = _create_blackboard_accessor_from_blackboard(
                        blackboard=new_blackboard
                    )
                    console.print("(Blackboard loaded)")
                continue
            case CommandAction.no_action:
                pass
            case _:
                raise RuntimeError(f"Not a recognised CommandAction: {action}")

        blackboard = generate(
            agent_definitions=agent_definitions,
            chat_agent_description=chat_agent_description,
            _config=_config,
            user_prompt=user_prompt,
            blackboard=blackboard,
        )

        if given_user_prompt:
            break
    # To support a stateless web service, we return the whole blackboard, and accept it as optional input
    return blackboard


# to debug - see agent.system_prompt_generator.generate_prompt()
