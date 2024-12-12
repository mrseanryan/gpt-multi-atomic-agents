from abc import abstractmethod
import typing
from atomic_agents.agents.base_agent import (
    BaseIOSchema,
)
from pydantic import Field

from .graphql_dto import (
    GraphQLAgentInputSchema,
    GraphQLAgentOutputSchema,
    ParamNameToValues,
)

from .system_prompt_builders import (
    FunctionSystemPromptBuilder,
    GraphQLSystemPromptBuilder,
    SystemPromptBuilderBase,
)
from .util_pydantic import CustomBaseModel

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


class AgentDefinitionBase(CustomBaseModel):
    """
    Defines one function-based agent. NOT for direct use with LLM.
    """

    agent_name: str = Field(
        description="The name of the agent.", examples=["Creature Creator"]
    )
    description: str = Field(
        description="Describes the function of the agent. This acts as a mini prompt for the LLM."
    )
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

    @abstractmethod
    def get_agent_parameters(self) -> ParamNameToValues:
        raise NotImplementedError


class FunctionAgentDefinition(AgentDefinitionBase):
    input_schema: type[FunctionAgentInputSchema]
    initial_input: FunctionAgentInputSchema
    output_schema: type[FunctionAgentOutputSchema]

    accepted_functions: list[FunctionSpecSchema] = Field(
        description="The set of Function Calls which this agent can understand as input."
    )

    def _cast_blackboard(self, blackboard: Blackboard) -> FunctionCallBlackboard:
        if not isinstance(blackboard, FunctionCallBlackboard):
            raise RuntimeError("Expected blackboard to be a FunctionCallBlackboard")
        return typing.cast(FunctionCallBlackboard, blackboard)

    def _cast_response(self, response: BaseIOSchema) -> FunctionAgentOutputSchema:
        if not isinstance(response, FunctionAgentOutputSchema):
            raise RuntimeError("Expected response to be a FunctionAgentOutputSchema")
        return typing.cast(FunctionAgentOutputSchema, response)

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
        return self.initial_input.topics

    def get_agent_parameters(self) -> ParamNameToValues:
        return self.initial_input.agent_parameters

    def get_system_prompt_builder(self, _config: Config) -> SystemPromptBuilderBase:
        return FunctionSystemPromptBuilder(
            topics=self.get_topics(),
            _config=_config,
            allowed_functions_to_generate=self.initial_input.functions_allowed_to_generate,
        )

    def update_blackboard(self, response: BaseIOSchema, blackboard: Blackboard) -> None:
        function_response = self._cast_response(response)
        function_blackboard = self._cast_blackboard(blackboard)
        function_blackboard.add_mesage(
            Message(role=MessageRole.assistant, message=function_response.chat_message)
        )
        function_blackboard.add_generated_functions(
            function_response.generated_function_calls
        )


def build_function_agent_definition(
    agent_name: str,
    description: str,
    accepted_functions: list[FunctionSpecSchema],
    functions_allowed_to_generate: list[FunctionSpecSchema],
    topics: list[str],
    agent_parameters: ParamNameToValues | None = None,
) -> FunctionAgentDefinition:
    if not agent_parameters:
        agent_parameters = {}
    return FunctionAgentDefinition(
        agent_name=agent_name,
        description=description,
        accepted_functions=accepted_functions,
        input_schema=FunctionAgentInputSchema,
        initial_input=FunctionAgentInputSchema(
            functions_allowed_to_generate=functions_allowed_to_generate,
            previously_generated_functions=[],
            topics=topics,
            agent_parameters=agent_parameters,
        ),
        output_schema=FunctionAgentOutputSchema,
    )


class GraphQLAgentDefinition(AgentDefinitionBase):
    input_schema: type[GraphQLAgentInputSchema]
    initial_input: GraphQLAgentInputSchema
    output_schema: type[GraphQLAgentOutputSchema]

    accepted_graphql_schemas: list[str] = Field(
        description="The set of GraphQL schemas which the agent can use to work with client data."
    )

    def _cast_blackboard(self, blackboard: Blackboard) -> GraphQLBlackboard:
        if not isinstance(blackboard, GraphQLBlackboard):
            raise RuntimeError("Expected blackboard to be a GraphQLBlackboard")
        graphql_blackboard = typing.cast(GraphQLBlackboard, blackboard)
        return graphql_blackboard

    def _cast_response(self, response: BaseIOSchema) -> GraphQLAgentOutputSchema:
        if not isinstance(response, GraphQLAgentOutputSchema):
            raise RuntimeError("Expected response to be a GraphQLAgentOutputSchema")
        return typing.cast(GraphQLAgentOutputSchema, response)

    def build_input(
        self, rewritten_user_prompt: str, blackboard: Blackboard, config: Config
    ) -> BaseIOSchema:
        graphql_blackboard = self._cast_blackboard(blackboard)

        initial_input = self.initial_input

        initial_input.user_input = rewritten_user_prompt
        initial_input.graphql_data = graphql_blackboard.get_user_data()

        initial_input.previously_generated_mutations = (
            graphql_blackboard.get_generated_mutations_matching(
                self.accepted_graphql_schemas
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

    def get_agent_parameters(self) -> ParamNameToValues:
        return self.initial_input.agent_parameters

    def update_blackboard(self, response: BaseIOSchema, blackboard: Blackboard) -> None:
        graphql_blackboard = self._cast_blackboard(blackboard)
        graphql_response = self._cast_response(response)

        graphql_blackboard.add_generated_mutations(graphql_response.generated_mutations)
        graphql_blackboard.add_mesage(
            Message(role=MessageRole.assistant, message=graphql_response.chat_message)
        )


def build_graphql_agent_definition(
    agent_name: str,
    description: str,
    accepted_graphql_schemas: list[str],
    mutations_allowed_to_generate: list[str],
    topics: list[str],
    agent_parameters: ParamNameToValues | None = None,
) -> GraphQLAgentDefinition:
    if not agent_parameters:
        agent_parameters = {}
    return GraphQLAgentDefinition(
        agent_name=agent_name,
        description=description,
        accepted_graphql_schemas=accepted_graphql_schemas,
        input_schema=GraphQLAgentInputSchema,
        initial_input=GraphQLAgentInputSchema(
            graphql_data="",
            mutations_allowed_to_generate=mutations_allowed_to_generate,
            previously_generated_mutations=[],
            topics=topics,
            agent_parameters=agent_parameters,
        ),
        output_schema=GraphQLAgentOutputSchema,
    )
