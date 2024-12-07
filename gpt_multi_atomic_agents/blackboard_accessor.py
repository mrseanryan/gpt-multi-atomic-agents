from dataclasses import dataclass, field

from gpt_multi_atomic_agents.functions_dto import FunctionCallSchema
from .blackboard import FunctionCallBlackboard, GraphQLBlackboard, Message


@dataclass
class FunctionCallBlackboardAccessor:
    """Accessor for client to simplify integration and update of the Blackboard."""

    _blackboard: FunctionCallBlackboard = field(
        default_factory=lambda: FunctionCallBlackboard()
    )  # The inner blackboard - should only be accessed by the framework, not the client

    def get_new_functions(self) -> list[FunctionCallSchema]:
        """Get the new function calls which the client needs to execute. After executing, the client should call update_with_new_client_data() to pass in the updated and/or missing data."""
        return self._blackboard.internal_newly_generated_functions

    def get_new_messages(self) -> list[Message]:
        """Gets newly created messages that should be displayed to the user."""
        return self._blackboard.internal_newly_generated_messages

    def update_with_new_client_data(
        self, new_client_functions_representing_data: list[FunctionCallSchema]
    ) -> None:
        """Update the blackboard with the updated client data, to prepare for a new generation."""
        self._blackboard.set_user_data(user_data=new_client_functions_representing_data)


@dataclass
class MutationsAndQueries:
    previously_generated_mutation_calls: list[str] = field(default_factory=list)
    previously_generated_queries: list[str] = field(default_factory=list)


@dataclass
class GraphQLBlackboardAccessor:
    """Accessor for client to simplify integration and update of the Blackboard."""

    _blackboard: GraphQLBlackboard = field(
        default_factory=lambda: GraphQLBlackboard()
    )  # The inner blackboard - should only be accessed by the framework, not the client

    def get_new_mutations_and_queries(self) -> MutationsAndQueries:
        """Get the new mutations and queries which the client needs to execute. After executing, the client should call update_with_new_client_data() to pass in the updated and/or missing data."""
        queries = []  # TODO update when we add generation of GraphQL queries
        return MutationsAndQueries(
            previously_generated_mutation_calls=self._blackboard.internal_previously_generated_mutation_calls,
            previously_generated_queries=queries,
        )

    def get_new_messages(self) -> list[Message]:
        """Gets newly created messages that should be displayed to the user."""
        return self._blackboard.internal_newly_generated_messages

    def update_with_new_client_data(self, user_data: str) -> None:
        """Update the blackboard with the updated client data, to prepare for a new generation."""
        self._blackboard.set_user_data(user_data)


BlackboardAccessor = FunctionCallBlackboardAccessor | GraphQLBlackboardAccessor
