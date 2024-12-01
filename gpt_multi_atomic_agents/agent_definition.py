from abc import abstractmethod
from dataclasses import dataclass
import typing
from atomic_agents.agents.base_agent import (
    BaseIOSchema,
)

from .graphql_dto import GraphQLAgentInputSchema, GraphQLAgentOutputSchema

from .system_prompt_builders import (
    FunctionSystemPromptBuilder,
    GraphQLSystemPromptBuilder,
    SystemPromptBuilderBase,
)

from . import util_output
from .blackboard import (
    Blackboard,
    FunctionCallBlackboard,
    GraphQLBlackboard,
    Message,
    MessageRole,
)
from .config import Config

from .functions_dto import (
    FunctionAgentInputSchema,
    FunctionAgentOutputSchema,
    FunctionSpecSchema,
)


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
    # TODO: could add custom prompt/prompt-extension if needed

    @abstractmethod
    def build_input(
        self, rewritten_user_prompt: str, blackboard: Blackboard, config: Config
    ) -> BaseIOSchema:
        raise NotImplementedError

    @abstractmethod
    def get_system_prompt_builder(self, _config: Config) -> SystemPromptBuilderBase:
        raise NotImplementedError

    @abstractmethod
    def update_blackboard(self, response: BaseIOSchema, blackboard: Blackboard) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_topics(self) -> list[str]:
        raise NotImplementedError


@dataclass
class FunctionAgentDefinition(AgentDefinitionBase):
    input_schema: type[FunctionAgentInputSchema]
    initial_input: FunctionAgentInputSchema
    output_schema: type[FunctionAgentOutputSchema]
    accepted_functions: list[FunctionSpecSchema]
    topics: list[str]  # The agent ONLY generates if user mentioned one of these topics

    def _cast_blackboard(self, blackboard: Blackboard) -> FunctionCallBlackboard:
        if not isinstance(blackboard, FunctionCallBlackboard):
            raise RuntimeError("Expected blackboard to be a FunctionCallBlackboard")
        function_blackboard = typing.cast(FunctionCallBlackboard, blackboard)
        return function_blackboard

    def build_input(
        self, rewritten_user_prompt: str, blackboard: Blackboard, config: Config
    ) -> BaseIOSchema:
        function_blackboard = self._cast_blackboard(blackboard)

        initial_input = self.initial_input
        initial_input.user_input = rewritten_user_prompt

        initial_input.previously_generated_functions = (
            function_blackboard.get_generated_functions_matching(
                self.get_accepted_function_names()
            )
        )
        util_output.print_debug(
            f"[{self.agent_name}] Previously generated funs: {initial_input.previously_generated_functions}",
            config,
        )

        return initial_input

    def get_accepted_function_names(self) -> list[str]:
        return [f.function_name for f in self.accepted_functions]

    def get_topics(self) -> list[str]:
        return self.topics

    def get_system_prompt_builder(self, _config: Config) -> SystemPromptBuilderBase:
        return FunctionSystemPromptBuilder(
            topics=self.topics,
            _config=_config,
            allowed_functions_to_generate=self.initial_input.functions_allowed_to_generate,
        )

    def update_blackboard(self, response: BaseIOSchema, blackboard: Blackboard) -> None:
        function_blackboard = self._cast_blackboard(blackboard)
        function_blackboard.add_generated_functions(response.generated_function_calls)


@dataclass
class GraphQLAgentDefinition(AgentDefinitionBase):
    input_schema: type[GraphQLAgentInputSchema]
    initial_input: GraphQLAgentInputSchema
    output_schema: type[GraphQLAgentOutputSchema]

    def _cast_blackboard(self, blackboard: Blackboard) -> GraphQLBlackboard:
        if not isinstance(blackboard, GraphQLBlackboard):
            raise RuntimeError("Expected blackboard to be a GraphQLBlackboard")
        graphql_blackboard = typing.cast(GraphQLBlackboard, blackboard)
        return graphql_blackboard

    def build_input(
        self, rewritten_user_prompt: str, blackboard: Blackboard, config: Config
    ) -> BaseIOSchema:
        graphql_blackboard = self._cast_blackboard(blackboard)

        initial_input = self.initial_input

        initial_input.user_input = rewritten_user_prompt
        initial_input.graphql_data = graphql_blackboard.get_user_data()

        initial_input.previously_generated_mutations = (
            graphql_blackboard.get_generated_mutations_matching(
                initial_input.accepted_graphql_schemas
            )
        )
        util_output.print_debug(
            f"[{self.agent_name}] build_input(): {initial_input}", config
        )
        util_output.print_debug(
            f"[{self.agent_name}] Matching previously generated mutations: {initial_input.previously_generated_mutations}",
            config,
        )

        return initial_input

    def get_system_prompt_builder(self, _config: Config) -> SystemPromptBuilderBase:
        return GraphQLSystemPromptBuilder(_config=_config)

    def get_topics(self) -> list[str]:
        return self.initial_input.topics

    def update_blackboard(self, response: BaseIOSchema, blackboard: Blackboard) -> None:
        graphql_blackboard = self._cast_blackboard(blackboard)
        graphql_blackboard.add_generated_mutations(response.generated_mutations)
        graphql_blackboard.add_mesage(
            Message(role=MessageRole.assistant, message=response.chat_message)
        )
