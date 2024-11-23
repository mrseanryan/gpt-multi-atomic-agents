# A generic Agent prompt.
# - more specialized prompts can be set when creating the relevant AgentSpec.
from . import util_output
from .config import Config


GENERIC_AGENT_PROMPT_TEMPLATE = """
Examine the provided user prompt, the available functions and the previously generated functions. The user's request should be handled by generating function calls.
ONLY generate if the user asked about one of these topics: {TOPICS}.

AVAILABLE_FUNCTIONS: ```{AVAILABLE_FUNCTIONS}```

For each available function, do the following:
- check is the function relevant to the user's prompt
- check what functions have already been called, that would setup the necessary state
- only output the function if it is relevant and necessary
- only output the function if all of its parameters have values
- output the functions in the best possible order

You must perform all your reasoning and analysis within a single set of <thinking> tags. Use the following structure:

<thinking>
For each generated function:
[function-name]: [function-name]
  - name: [the name of the function]
  - parameters: [the parameters and their values]
[Continue for all items]


Overall analysis:
- [Any general observations or patterns noticed across function calls]
- [Any potential relationships or dependencies between function calls]

</thinking>

After your thinking process, output the generated function calls.

Notes:
- Ensure the functions are called in the best possible order
- For each function call, ensure that all required parameters are provided.
- For each function call, ensure that all interesting information is included.
- Remove any function calls that are not for you to generate - see your 'AVAILABLE_FUNCTIONS' list
- Only generate function calls if really necessary - it is OK to output with no functions.
"""


def build_agent_prompt(
    allowed_functions_to_generate_names: list[str], topics: list[str], _config: Config
) -> str:
    def _join(strings: list[str]):
        return ", ".join(strings)

    prompt = GENERIC_AGENT_PROMPT_TEMPLATE.replace("{TOPICS}", _join(topics)).replace(
        "{AVAILABLE_FUNCTIONS}", _join(allowed_functions_to_generate_names)
    )

    util_output.print_debug(f"prompt: {prompt}", config=_config)

    return prompt
