from parameterized import parameterized
import unittest

from rich.console import Console

from . import main

console = Console()


class TestSimLifeViaGraphQL(unittest.TestCase):
    @parameterized.expand(
        [
            (
                "test: Add cow, grass, human.",
                "Add a cow that eats grass. Add a human - the cow feeds the human. Add alien that eats the human. The human also eats cows.",
                "",
                3,
            ),
            (
                "test: Add cow, grass - with human already in data.",
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
                2,  # Human already exists
            ),
        ]
    )
    def test_generate_creatures_via_graphql(
        self,
        _test_name_implicitly_used: str,
        user_prompt: str,
        user_data: str,
        expected_add_creature_calls: int,
    ) -> None:
        # Arrange

        # Act
        console.print(f"PROMPT: {user_prompt}")
        result = main.run_chat_loop(user_prompt=user_prompt, user_data=user_data)
        console.print("FINAL OUTPUT (GraphQL mutations):")
        console.print(result)

        # Assert
        self.assertGreater(len(result), 0)

        result_joined = ",".join(result)
        actual_add_creature_calls = result_joined.count('creature_name: "')
        self.assertEqual(expected_add_creature_calls, actual_add_creature_calls)
