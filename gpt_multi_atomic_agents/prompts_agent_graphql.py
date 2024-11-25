# A generic Agent prompt.
# TODO: more specialized prompts can be set when creating the relevant AgentDefinition.


GENERIC_AGENT_PROMPT_TEMPLATE = """
Examine the provided user prompt, the available GraphQL mutation definitions, the graphql_input data and the previously generated GraphQL mutations. The user's request should be handled by generating GraphQL mutations.
ONLY generate if the user asked about one of the agent topics.

For each available mutation, do the following:
- check is the mutation relevant to the user's prompt
- check the existing graphql_data and what mutations have already been called, that would setup the necessary state
- only output the mutation if it is relevant and necessary
- only output the mutation if all of its parameters have values
- output the mutations in the best possible order

You must perform all your reasoning and analysis within a single set of <thinking> tags. Use the following structure:

<thinking>
For each generated mutation:
[mutation-name]: [mutation-name]
  - name: [the name of the mutation]
  - parameters: [the parameters and their values]
[Continue for all items]


Overall analysis:
- [Any general observations or patterns noticed across mutation calls]
- [Any potential relationships or dependencies between mutation calls and also the existing GraphQL data]

</thinking>

After your thinking process, output only the necessary generated mutation calls.

Notes:
- Ensure the mutations are called in the best possible order
- For each mutation call, ensure that all required parameters are provided.
- For each mutation call, ensure that all interesting information is included.
- Remove any mutation calls that are not for you to generate - see your 'AVAILABLE_MUTATIONS'.
- Only generate mutations if really necessary - check against the input graphql_data. It is OK to output with no mutations.
"""


def build_agent_prompt() -> str:
    return GENERIC_AGENT_PROMPT_TEMPLATE
