from gpt_multi_atomic_agents import config, main_service
from gpt_multi_atomic_agents.blackboard import GraphQLBlackboard
from . import agents


def run_chat_loop_via_graphql(
    user_prompt: str | None = None, user_data: str = ""
) -> list[str]:
    CHAT_AGENT_DESCRIPTION = (
        "Handles users questions about an ecosystem game like Sim Life"
    )

    agent_definitions = [
        agents.build_creature_agent(),
        agents.build_relationship_agent(),
        agents.build_vegatation_agent(),
    ]

    # TODO read from config.ini
    _config = config.Config(
        ai_platform=config.AI_PLATFORM_Enum.bedrock_anthropic,
        model=config.ANTHROPIC_MODEL,
        max_tokens=config.ANTHROPIC_MAX_TOKENS,
        is_debug=False,
    )

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
