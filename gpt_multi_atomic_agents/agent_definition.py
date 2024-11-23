from abc import abstractmethod
from dataclasses import dataclass
from atomic_agents.agents.base_agent import (
    BaseIOSchema,
)
from pydantic import Field

from .graphql_dto import GraphQLAgentInputSchema, GraphQLAgentOutputSchema

from .system_prompt_builders import FunctionSystemPromptBuilder, GraphQLSystemPromptBuilder, SystemPromptBuilderBase

from . import util_output
from .blackboard import Blackboard
from .config import Config

from .functions_dto import FunctionAgentInputSchema, FunctionAgentOutputSchema, FunctionSpecSchema

@dataclass
class AgentDefinitionBase:
    """
    Defines one function-based agent. NOT for direct use with LLM.
    """
    agent_name: str
    description: str
    input_schema: type[BaseIOSchema]
    initial_input: BaseIOSchema
    output_schema: type[BaseIOSchema]
    topics: list[str] # The agent ONLY generates if user mentioned one of these topics
    # TODO: could add custom prompt/prompt-extension if needed

    @abstractmethod
    def build_input(self, user_input: str, blackboard: Blackboard, config: Config) -> BaseIOSchema:
        raise NotImplementedError

    @abstractmethod
    def get_system_prompt_builder(self, _config: Config) -> SystemPromptBuilderBase:
        raise NotImplementedError

    @abstractmethod
    def update_blackboard(self, response: BaseIOSchema, blackboard: Blackboard) -> None:
        raise NotImplementedError

@dataclass
class FunctionAgentDefinition(AgentDefinitionBase):
    input_schema: type[FunctionAgentInputSchema]
    initial_input: FunctionAgentInputSchema
    output_schema: type[FunctionAgentOutputSchema]
    accepted_functions: list[FunctionSpecSchema]

    def get_accepted_function_names(self) -> list[str]:
        return [f.function_name for f in self.accepted_functions]

    def build_input(self, user_input: str, blackboard: Blackboard, config: Config) -> BaseIOSchema:
        initial_input = self.initial_input
        initial_input.user_input = user_input

        initial_input.previously_generated_functions = blackboard.get_generated_functions_matching(self.get_accepted_function_names())
        util_output.print_debug(f"[{self.agent_name}] Previously generated funs: {initial_input.previously_generated_functions}", config)

        return initial_input

    def get_system_prompt_builder(self, _config: Config) -> SystemPromptBuilderBase:
        return FunctionSystemPromptBuilder(topics=self.topics, _config=_config, allowed_functions_to_generate=self.initial_input.functions_allowed_to_generate)

    def update_blackboard(self, response: BaseIOSchema, blackboard: Blackboard) -> None:
        if isinstance(response, FunctionAgentOutputSchema):
            blackboard.add_generated_functions(response.generated_function_calls)
        else:
            raise RuntimeError("Unexpected response type - expected a FunctionAgentOutputSchema")

@dataclass
class GraphQLAgentDefinition(AgentDefinitionBase):
    input_schema: type[GraphQLAgentInputSchema]
    initial_input: GraphQLAgentInputSchema
    output_schema: type[GraphQLAgentOutputSchema]
    accepted_graphql_schemas: list[str]

    def build_input(self, user_input: str, blackboard: Blackboard, config: Config) -> BaseIOSchema:
        initial_input = self.initial_input
        initial_input.user_input = user_input

        initial_input.previously_generated_mutations = blackboard.get_generated_mutations_matching(self.accepted_graphql_schemas)
        util_output.print_debug(f"[{self.agent_name}] Matching previously generated mutations: {initial_input.previously_generated_mutations}", config)

        return initial_input

    def get_system_prompt_builder(self, _config: Config) -> SystemPromptBuilderBase:
        return GraphQLSystemPromptBuilder(topics=self.topics, _config=_config, mutations_allowed_to_generate=self.initial_input.mutations_allowed_to_generate)

    def update_blackboard(self, response: BaseIOSchema, blackboard: Blackboard) -> None:
        if isinstance(response, GraphQLAgentOutputSchema):
            blackboard.add_generated_mutations(response.generated_mutations)
        else:
            raise RuntimeError("Unexpected response type - expected a GraphQLAgentOutputSchema")
