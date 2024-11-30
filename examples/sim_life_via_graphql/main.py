from gpt_multi_atomic_agents import config, main_service
from gpt_multi_atomic_agents.blackboard import GraphQLBlackboard
from . import agents


def get_default_config(delay_between_calls_in_seconds: float = 0.0):
    # TODO read from config.ini
    _config = config.Config(
        ai_platform=config.AI_PLATFORM_Enum.bedrock_anthropic,
        model=config.ANTHROPIC_MODEL,
        max_tokens=config.ANTHROPIC_MAX_TOKENS,
        is_debug=False,
        delay_between_calls_in_seconds=delay_between_calls_in_seconds,
    )
    return _config


CHAT_AGENT_DESCRIPTION = "Handles users questions about an ecosystem game like Sim Life"

agent_definitions = [
    agents.build_creature_agent(),
    agents.build_relationship_agent(),
    agents.build_vegatation_agent(),
]


def run_chat_loop_via_graphql(
    user_prompt: str | None = None,
    user_data: str = "",
    _config: config.Config | None = None,
) -> list[str]:
    if not _config:
        _config = get_default_config()

    initial_blackboard = GraphQLBlackboard(previously_generated_mutation_calls=[])
    initial_blackboard.set_user_data(user_data=user_data)
    blackboard = main_service.run_chat_loop(
        agent_definitions=agent_definitions,
        chat_agent_description=CHAT_AGENT_DESCRIPTION,
        _config=_config,
        given_user_prompt=user_prompt,
        blackboard=initial_blackboard,
    )
    return blackboard.previously_generated_mutation_calls


if __name__ == "__main__":
    run_chat_loop_via_graphql()
