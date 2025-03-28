import agents
from gpt_multi_atomic_agents import config, main_generator, blackboard_accessor

from importlib.metadata import version

gmaa_version = version("gpt_multi_atomic_agents")
print(f"Using gpt_multi_atomic_agents [{gmaa_version}] - 'from X import Y'")


def run_chat_loop_via_function_calls(
    test_prompt: str | None = None,
) -> blackboard_accessor.BlackboardAccessor:
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

    blackboard = main_generator.run_chat_loop(
        agent_definitions=agent_definitions,
        chat_agent_description=CHAT_AGENT_DESCRIPTION,
        _config=_config,
        given_user_prompt=test_prompt,
    )
    print(blackboard)
    return blackboard


if __name__ == "__main__":
    run_chat_loop_via_function_calls(
        "Add a cow that eats grass. Add a human - the cow feeds the human. Add alien that eats the human. The human also eats cows.",
    )
