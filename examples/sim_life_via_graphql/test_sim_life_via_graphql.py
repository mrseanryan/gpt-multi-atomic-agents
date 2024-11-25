from cornsnake import util_wait
from parameterized import parameterized
import unittest

from rich.console import Console

from . import main

console = Console()

DELAY_SECONDS_BETWEEN_CALLS_TO_AVOID_RATE_LIMIT = 5
DELAY_SECONDS_BETWEEN_TESTS_TO_AVOID_RATE_LIMIT = 10


class TestSimLifeViaGraphQL(unittest.TestCase):
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
        result = main.run_chat_loop_via_graphql(
            user_prompt=user_prompt, user_data=user_data, _config=_config
        )
        console.print("FINAL OUTPUT (GraphQL mutations):")
        console.print(result)

        # Assert
        self.assertGreater(len(result), 0)

        result_joined = ",".join(result)

        mutation_errors = []
        for mutation in expected_mutation_counts.keys():
            actual_count = result_joined.count(mutation)
            expected_count = expected_mutation_counts[mutation]
            if actual_count != expected_count:
                mutation_errors.append(
                    f"Expected {expected_count} {mutation} calls but received {actual_count}"
                )
        self.assertEqual([], mutation_errors)
        util_wait.wait_seconds(DELAY_SECONDS_BETWEEN_TESTS_TO_AVOID_RATE_LIMIT)
