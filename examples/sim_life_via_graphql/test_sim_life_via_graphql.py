from parameterized import parameterized
import unittest

from rich.console import Console

from . import main

console = Console()

class TestSimLifeViaGraphQL(unittest.TestCase):
    @parameterized.expand(
        [
            ("test: Add cow, grass, human.", 
                "Add a cow that eats grass. Add a human - the cow feeds the human. Add alien that eats the human. The human also eats cows.",
             )
        ]
    )
    def test_generate_creatures_via_graphql(
        self,
        _test_name_implicitly_used: str,
        prompt: str
    ) -> None:
        # Arrange

        # Act
        console.print(f"PROMPT: {prompt}")
        result = main.run_chat_loop(prompt)
        console.print("FINAL OUTPUT (GraphQL mutations):")
        console.print(result)

        # Assert
        self.assertGreater(len(result), 0)
