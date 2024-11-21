from gpt_multi_atomic_agents import functions_expert_service
from . import agents

def run_chat_loop(test_prompt: str|None = None) -> list:
    CHAT_AGENT_DESCRIPTION = "Handles users questions about an ecosystem game like Sim Life"

    agent_definitions = [
        agents.build_creature_agent(), agents.build_relationship_agent(), agents.build_vegatation_agent()
    ]

    return functions_expert_service.run_chat_loop(agent_definitions=agent_definitions, chat_agent_description=CHAT_AGENT_DESCRIPTION, test_prompt=test_prompt)

if __name__ == "__main__":
    run_chat_loop()
