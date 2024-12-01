from dataclasses import dataclass, field
from enum import StrEnum, auto
import logging

from .functions_dto import FunctionCallSchema
from . import util_graphql

logger = logging.getLogger(__file__)


class MessageRole(StrEnum):
    user = auto()
    assistant = auto()


@dataclass
class Message:
    role: MessageRole
    message: str


@dataclass
class FunctionCallBlackboard:
    # All previously generated functions: either from client (representing its data) or from agents in this generation
    _previously_generated_functions: list[FunctionCallSchema] = field(
        default_factory=list
    )
    # All previous messages in this chat (series of generations)
    _previous_messages: list[Message] = field(default_factory=list)

    # Messages that were newly-generated during this generation (required for client to know what new messages to display)
    _newly_generated_messages: list[Message] = field(default_factory=list)

    # Functions that were newly-generated during this generation (required for client so they know what functions they need to execute to update their data).
    _newly_generated_functions: list[FunctionCallSchema] = field(default_factory=list)

    def add_generated_functions(
        self, generated_function_calls: list[FunctionCallSchema]
    ) -> None:
        self._previously_generated_functions += generated_function_calls
        self._newly_generated_functions += generated_function_calls

    def get_generated_functions_matching(
        self, function_names: list[str]
    ) -> list[FunctionCallSchema]:
        return list(
            filter(
                lambda f: f.function_name in function_names,
                self._previously_generated_functions,
            )
        )

    def add_mesage(self, message: Message) -> None:
        self._previous_messages.append(message)
        self._newly_generated_messages.append(message)

    def _reset(self):
        """Resets newly created functions, to prepare for next generation"""
        self._newly_generated_functions.clear()
        self._newly_generated_messages.clear()

    def set_user_data(self, user_data: list[FunctionCallSchema]) -> None:
        """Receives the new version of user data, by setting the function-calls list, so is ready for next generation."""
        self._reset()
        self._previously_generated_functions = user_data


@dataclass
class GraphQLBlackboard:
    # Previously generated mutation calls, in this generation. Cleared out when new client data is received.
    _previously_generated_mutation_calls: list[str] = field(default_factory=list)

    # All previous messages in this chat (series of generations)
    _previous_messages: list[Message] = field(default_factory=list)

    # Messages that were newly-generated during this generation (required for client to know what new messages to display)
    _newly_generated_messages: list[Message] = field(default_factory=list)

    # The user data at the start of this generation.
    _user_data: str = field(default="")

    def add_generated_mutations(self, generated_mutation_calls: list[str]) -> None:
        self._previously_generated_mutation_calls += generated_mutation_calls

    def add_mesage(self, message: Message) -> None:
        self._previous_messages.append(message)
        self._newly_generated_messages.append(message)

    def get_generated_mutations_matching(
        self, accepted_graphql_schemas: list[str]
    ) -> list[str]:
        """Filter the generated mutations to suit an agent's allowed input."""
        accepted_mutation_names = util_graphql.parse_out_mutation_names_from_schemas(
            accepted_graphql_schemas
        )

        return util_graphql.filter_to_matching_mutation_calls(
            self._previously_generated_mutation_calls, accepted_mutation_names
        )

    def get_user_data(self) -> str:
        return self._user_data

    def set_user_data(self, user_data: str) -> None:
        self._reset()
        self._user_data = user_data

    def _reset(self) -> None:
        """
        Clears out created mutations and queries, so is ready for next generation.
        """
        self._previously_generated_mutation_calls.clear()
        self._newly_generated_messages.clear()


Blackboard = FunctionCallBlackboard | GraphQLBlackboard
