from cornsnake import util_wait
from parameterized import parameterized
import unittest

from rich.console import Console

from . import main

console = Console()

DELAY_SECONDS_BETWEEN_CALLS_TO_AVOID_RATE_LIMIT = 5
DELAY_SECONDS_BETWEEN_TESTS_TO_AVOID_RATE_LIMIT = 10


class TestSimLife(unittest.TestCase):
    @parameterized.expand(
        [
            (
                "test: Add cow, grass, human.",
                "Add a cow that eats grass. Add a human - the cow feeds the human. Add alien that eats the human. The human also eats cows.",
            )
        ]
    )
    def test_generate_creatures_via_functions(
        self, _test_name_implicitly_used: str, prompt: str
    ) -> None:
        # Arrange
        _config = main.get_default_config(
            delay_between_calls_in_seconds=DELAY_SECONDS_BETWEEN_CALLS_TO_AVOID_RATE_LIMIT
        )

        # Act
        console.print(f"PROMPT: {prompt}")
        result = main.run_chat_loop_via_function_calls(prompt, _config=_config)
        console.print("FINAL OUTPUT (function calls):")
        console.print(result)

        # Assert
        self.assertGreater(len(result.get_new_functions()), 0)
        self.assertGreater(len(result.get_new_messages()), 0)
        util_wait.wait_seconds(DELAY_SECONDS_BETWEEN_TESTS_TO_AVOID_RATE_LIMIT)


# TODO add test via generate_plan() and generate()

# TODO add test to cover the client-side (BlackboardAccessor)
#
# note: normally after calling generate() the client would:
# - execute any functions to update their data
#   - for some functions this involves getting more data
# Then cycle around: ask user for prompt, update the blackboard, call generate_plan(), call generate()...
