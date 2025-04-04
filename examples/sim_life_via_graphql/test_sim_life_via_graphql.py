from cornsnake import util_wait
from parameterized import parameterized
import unittest

from rich.console import Console

from gpt_multi_atomic_agents import main_generator, main_router
from gpt_multi_atomic_agents.blackboard import GraphQLBlackboard, Message
from gpt_multi_atomic_agents.blackboard_accessor import GraphQLBlackboardAccessor

from . import main

console = Console()

DELAY_SECONDS_BETWEEN_CALLS_TO_AVOID_RATE_LIMIT = 5
DELAY_SECONDS_BETWEEN_TESTS_TO_AVOID_RATE_LIMIT = 10


class TestSimLifeViaGraphQL(unittest.TestCase):
    def _check_generation_result(
        self,
        blackboard: GraphQLBlackboardAccessor,
        expected_mutation_counts: dict[str, int],
    ) -> None:
        new_mutations_and_queries = blackboard.get_new_mutations_and_queries()
        self.assertGreater(
            len(new_mutations_and_queries.previously_generated_mutation_calls), 0
        )
        self.assertGreater(len(blackboard.get_new_messages()), 0)

        result_joined = ",".join(
            new_mutations_and_queries.previously_generated_mutation_calls
        )

        mutation_errors = []
        for mutation in expected_mutation_counts.keys():
            actual_count = result_joined.count(mutation)
            expected_count = expected_mutation_counts[mutation]
            if actual_count != expected_count:
                mutation_errors.append(
                    f"Expected {expected_count} {mutation} calls but received {actual_count}"
                )
        self.assertEqual([], mutation_errors)

    @parameterized.expand(
        [
            (
                "complex test: Add cow, grass, human, alien.",
                "Add a cow that eats grass. Add a human - the cow feeds the human. Add alien that eats the human. The human also eats cows.",
                "",
                {"addCreature(": 3, "addVegetation(": 1, "addCreatureRelationship(": 4},
            ),
            (
                "test: Add cow - with human already in GraphQL data.",
                "The cow feeds the human",
                """
                {
                id: "H001",
                creature_name: "Human",
                allowed_terrain: TerrainType.LAND,
                age: 30,
                icon_name: IconType.HUMAN
                }
                """,
                {
                    "addCreature(": 1,  # Human already exists
                    "addVegetation(": 0,
                    "addCreatureRelationship(": 1,
                },
            ),
            (
                "complex test: Add cow, grass, alien - with human already in GraphQL data.",
                "Add a cow that eats grass. The cow feeds the human. Add alien that eats the human. The human also eats cows.",
                """
                {
                id: "H001",
                creature_name: "Human",
                allowed_terrain: TerrainType.LAND,
                age: 30,
                icon_name: IconType.HUMAN
                }
                """,
                {
                    "addCreature(": 2,  # Human already exists
                    "addVegetation(": 1,
                    "addCreatureRelationship(": 4,
                },
            ),
        ]
    )
    def test_generate_creatures_via_graphql(
        self,
        _test_name_implicitly_used: str,
        user_prompt: str,
        user_data: str,
        expected_mutation_counts: dict[str, int],
    ) -> None:
        # Arrange

        # Act
        console.print(f"PROMPT: {user_prompt}")
        _config = main.get_default_config(
            delay_between_calls_in_seconds=DELAY_SECONDS_BETWEEN_CALLS_TO_AVOID_RATE_LIMIT
        )

        generation_result = main.run_chat_loop_via_graphql(
            user_prompt=user_prompt, user_data=user_data, _config=_config
        )
        console.print("FINAL OUTPUT (GraphQL mutations):")
        console.print(generation_result)

        # Assert
        self._check_generation_result(
            blackboard=generation_result,
            expected_mutation_counts=expected_mutation_counts,
        )

        util_wait.wait_seconds(DELAY_SECONDS_BETWEEN_TESTS_TO_AVOID_RATE_LIMIT)

    @parameterized.expand(
        [
            (
                "complex test: Add cow, grass, alien - with human already in GraphQL data.",
                "Add a cow that eats grass. The cow feeds the human. Add alien that eats the human. The human also eats cows.",
                3,
            ),
        ]
    )
    def test_generate_execution_plan_creatures_via_graphql(
        self,
        _test_name_implicitly_used: str,
        user_prompt: str,
        expected_agent_count: int,
    ):
        # Arrange

        # Act
        console.print(f"PROMPT: {user_prompt}")
        _config = main.get_default_config(
            delay_between_calls_in_seconds=DELAY_SECONDS_BETWEEN_CALLS_TO_AVOID_RATE_LIMIT
        )

        generation_result = main_router.generate_plan(
            agent_definitions=main.agent_definitions,
            chat_agent_description=main.CHAT_AGENT_DESCRIPTION,
            _config=_config,
            user_prompt=user_prompt,
        )
        console.print("FINAL OUTPUT (Execution Plan):")
        console.print(generation_result)

        # Assert
        self.assertEqual(
            len(generation_result.recommended_agents), expected_agent_count
        )

        util_wait.wait_seconds(DELAY_SECONDS_BETWEEN_TESTS_TO_AVOID_RATE_LIMIT)

    @parameterized.expand(
        [
            (
                "complex test [NO message history]: Add cow, grass, alien - with human already in GraphQL data.",
                "Add a cow that eats grass. The cow feeds the human. Add alien that eats the human. The human also eats cows.",
                [],
                """
                {
                    "creatures": [
                        {
                        "id": "H001",
                        "creature_name": "Human",
                        "allowed_terrain": "LAND",
                        "age": 30,
                        "icon_name": "HUMAN"
                        }
                    ],
                    "vegetations": [
                    ],
                    "relationships": [
                    ]
                }
                """,
                3,
                {
                    "addCreature(": 2,  # Human already exists
                    "addVegetation(": 1,
                    "addCreatureRelationship(": 4,
                },
            ),
            (
                "complex test [WITH message history]: Add alien - with human, cow, grass already in GraphQL data.",
                "Add alien that eats the human. The human also eats cows.",
                [
                    {
                        "role": "user",
                        "message": "Add a cow that eats grass. The cow feeds the human.",
                    },
                    {
                        "role": "assistant",
                        "message": "Sure! I will add a cow. The cow will eat grass and feed the human.",
                    },
                    {
                        "role": "user",
                        "message": "Add alien that eats the human. The human also eats cows.",
                    },
                ],
                """
                {
                    "creatures": [
                        {
                            "id": "H001",
                            "creature_name": "Human",
                            "allowed_terrain": "LAND",
                            "age": 30,
                            "icon_name": "HUMAN"
                        },
                        {
                            "id": "C001",
                            "creature_name": "Cow",
                            "allowed_terrain": "LAND",
                            "age": 4,
                            "icon_name": "OTHER_ICON"
                        },
                    ],
                    "vegetations": [
                        { "vegetation_name": "grass",      "icon_name": "GRASS_ICON",      "allowed_terrain": "LAND" }
                    ],
                    "relationships": [
                        {      "from_name": "Cow",      "to_name: "Grass",  "relationship_kind": "EATS" },
                        {      "from_name": "Cow",    "to_name": "Human",   "relationship_kind": "FEEDS" }
                    ]
                }
                """,
                2,
                {
                    "addCreature(": 1,  # Only the Alien is new
                    "addVegetation(": 0,
                    "addCreatureRelationship(": 2,
                },
            ),
        ]
    )
    def test_generate_execution_plan_then_generate_creatures_via_graphql(
        self,
        _test_name_implicitly_used: str,
        user_prompt: str,
        messages: list[Message],
        user_data: str,
        expected_agent_count: int,
        expected_mutation_counts: dict[str, int],
    ):
        # Arrange

        # Act
        console.print(f"PROMPT: {user_prompt}")
        _config = main.get_default_config(
            delay_between_calls_in_seconds=DELAY_SECONDS_BETWEEN_CALLS_TO_AVOID_RATE_LIMIT
        )

        execution_plan = main_router.generate_plan(
            agent_definitions=main.agent_definitions,
            chat_agent_description=main.CHAT_AGENT_DESCRIPTION,
            _config=_config,
            user_prompt=user_prompt,
            previous_plan=None,  # TODO (someone): Also test iterating over a previous plan
            messages=messages,
        )
        console.print("GENERATED OUTPUT (Execution Plan):")
        console.print(execution_plan)

        # Assert
        self.assertEqual(len(execution_plan.recommended_agents), expected_agent_count)

        util_wait.wait_seconds(DELAY_SECONDS_BETWEEN_TESTS_TO_AVOID_RATE_LIMIT)

        # Test: use the generated execution plan
        # Arrange
        initial_blackboard = GraphQLBlackboardAccessor(GraphQLBlackboard())
        initial_blackboard.update_with_new_client_data(user_data=user_data)

        # Act
        EMPTY_USER_PROMPT_TO_ENABLE_PLAN = ""
        generation_result = main_generator.generate(
            agent_definitions=main.agent_definitions,
            chat_agent_description=main.CHAT_AGENT_DESCRIPTION,
            _config=_config,
            user_prompt=EMPTY_USER_PROMPT_TO_ENABLE_PLAN,
            blackboard=initial_blackboard,
            execution_plan=execution_plan,
        )

        console.print("GENERATED OUTPUT (Generation):")
        console.print(generation_result)

        # Assert
        self._check_generation_result(
            blackboard=generation_result,
            expected_mutation_counts=expected_mutation_counts,
        )
        util_wait.wait_seconds(DELAY_SECONDS_BETWEEN_TESTS_TO_AVOID_RATE_LIMIT)


# TODO add test to cover the client-side (BlackboardAccessor)
#
# note: normally after generate() the client would:
# - execute any mutations to update their data
# - execute any queries to get more data
# Then cycle around: ask user for prompt, update the blackboard, call generate_plan(), call generate()...
