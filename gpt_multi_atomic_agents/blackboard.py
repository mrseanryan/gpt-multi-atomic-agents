from dataclasses import dataclass
from enum import StrEnum, auto

from pydantic import Field

from .util_pydantic import CustomBaseModel

from .functions_dto import FunctionCallSchema
from . import util_graphql
from . import rest_api_examples


class BlackboardFormat(StrEnum):
    function_call = auto()
    graphql = auto()


class MessageRole(StrEnum):
    user = auto()
    assistant = auto()


@dataclass
class Message:
    role: MessageRole
    message: str


class FunctionCallBlackboard(CustomBaseModel):
    format: BlackboardFormat = Field(
        description="The data format of the blackboard",
        default=BlackboardFormat.function_call,
    )

    internal_previously_generated_functions: list[FunctionCallSchema] = Field(
        description="All previously generated functions: either from client (representing its data) or from agents in this generation",
        examples=[[rest_api_examples.example_create_creature_call__wolf]],
        default_factory=list,
    )
    # All previous messages in this chat (series of generations)
    internal_previous_messages: list[Message] = Field(
        default_factory=list,
        examples=[
            [
                Message(role=MessageRole.user, message="Add a wolf"),
                Message(
                    role=MessageRole.assistant,
                    message="I have created a wolf. Is there anything else I can help you with?",
                ),
            ]
        ],
    )

    # Messages that were newly-generated during this generation (required for client to know what new messages to display)
    internal_newly_generated_messages: list[Message] = Field(
        default_factory=list, examples=[[]]
    )

    # Functions that were newly-generated during this generation (required for client so they know what functions they need to execute to update their data).
    internal_newly_generated_functions: list[FunctionCallSchema] = Field(
        default_factory=list, examples=[[]]
    )

    def add_generated_functions(
        self, generated_function_calls: list[FunctionCallSchema]
    ) -> None:
        self.internal_previously_generated_functions += generated_function_calls
        self.internal_newly_generated_functions += generated_function_calls

    def get_generated_functions_matching(
        self, function_names: list[str]
    ) -> list[FunctionCallSchema]:
        return list(
            filter(
                lambda f: f.function_name in function_names,
                self.internal_previously_generated_functions,
            )
        )

    def add_mesage(self, message: Message) -> None:
        self.internal_previous_messages.append(message)
        self.internal_newly_generated_messages.append(message)

    def add_previous_mesage(self, message: Message) -> None:
        self.internal_previous_messages.append(message)

    def reset_all(self) -> None:
        """
        Completely clears out the blackboard, starting over.
        """
        self.internal_previously_generated_functions.clear()
        self.internal_previous_messages.clear()
        self.internal_newly_generated_messages.clear()
        self.internal_newly_generated_functions.clear()

    def _reset(self):
        """Resets newly created functions, to prepare for next generation"""
        self.internal_newly_generated_functions.clear()
        self.internal_newly_generated_messages.clear()

    def reset_newly_generated(self) -> None:
        """Reset newly generated, in case client did not clear out"""
        self._reset()

    def set_user_data(self, user_data: list[FunctionCallSchema]) -> None:
        """Receives the new version of user data, by setting the function-calls list, so is ready for next generation."""
        self._reset()
        self.internal_previously_generated_functions = user_data


class GraphQLBlackboard(CustomBaseModel):
    format: BlackboardFormat = Field(
        description="The data format of the blackboard",
        default=BlackboardFormat.graphql,
    )

    # Previously generated mutation calls, in this generation. Cleared out when new client data is received (so is effectively *newly* generated only).
    internal_previously_generated_mutation_calls: list[str] = Field(
        default_factory=list
    )

    # All previous messages in this chat (series of generations)
    internal_previous_messages: list[Message] = Field(default_factory=list)

    # Messages that were newly-generated during this generation (required for client to know what new messages to display)
    internal_newly_generated_messages: list[Message] = Field(default_factory=list)

    # The user data at the start of this generation.
    internal_user_data: str = Field(default="")

    def add_generated_mutations(self, generated_mutation_calls: list[str]) -> None:
        self.internal_previously_generated_mutation_calls += generated_mutation_calls

    def add_mesage(self, message: Message) -> None:
        self.internal_previous_messages.append(message)
        self.internal_newly_generated_messages.append(message)

    def add_previous_mesage(self, message: Message) -> None:
        self.internal_previous_messages.append(message)

    def get_generated_mutations_matching(
        self, accepted_graphql_schemas: list[str]
    ) -> list[str]:
        """Filter the generated mutations to suit an agent's allowed input."""
        accepted_mutation_names = util_graphql.parse_out_mutation_names_from_schemas(
            accepted_graphql_schemas
        )

        return util_graphql.filter_to_matching_mutation_calls(
            self.internal_previously_generated_mutation_calls, accepted_mutation_names
        )

    def get_user_data(self) -> str:
        return self.internal_user_data

    def set_user_data(self, user_data: str) -> None:
        self._reset()
        self.internal_user_data = user_data

    def reset_all(self) -> None:
        """
        Completely clears out the blackboard, starting over.
        """
        self.internal_previously_generated_mutation_calls.clear()
        self.internal_previous_messages.clear()
        self.internal_newly_generated_messages.clear()
        self.internal_user_data = ""

    def _reset(self) -> None:
        """
        Clears out created mutations and queries, so is ready for next generation.
        """
        self.internal_previously_generated_mutation_calls.clear()
        self.internal_newly_generated_messages.clear()

    def reset_newly_generated(self) -> None:
        """Reset newly generated, in case client did not clear out"""
        self._reset()


Blackboard = FunctionCallBlackboard | GraphQLBlackboard
