from dataclasses import dataclass
from atomic_agents.agents.base_agent import (
    BaseIOSchema,
)
from pydantic import Field

from . import util_output
from .blackboard import Blackboard

from .functions_dto import FunctionAgentInputSchema, FunctionAgentOutputSchema, FunctionSpecSchema

@dataclass
class AgentDefinition:
    """
    Defines one agent. NOT for direct use with LLM.
    """
    agent_name: str
    description: str
    accepted_functions: list[FunctionSpecSchema]
    input_schema: type[FunctionAgentInputSchema]
    initial_input: FunctionAgentInputSchema
    output_schema: type[FunctionAgentOutputSchema]
    topics: list[str] = Field(description="This agent ONLY generates if user mentioned one of these topics")
    # TODO: could add custom prompt/prompt-extension if needed

    def build_input(self, user_input: str, blackboard: Blackboard) -> BaseIOSchema:
        initial_input = self.initial_input
        initial_input.user_input = user_input

        initial_input.previously_generated_functions = blackboard.get_generated_functions_matching(self.get_accepted_function_names())
        util_output.print_debug(f"[{self.agent_name}] Previously generated funs: {initial_input.previously_generated_functions}")

        return initial_input

    def get_accepted_function_names(self) -> list[str]:
        return [f.function_name for f in self.accepted_functions]
