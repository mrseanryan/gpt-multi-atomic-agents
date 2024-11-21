# gpt-multi-atomic-agents
A simple dynamic multi-agent framework based on [atomic-agents](https://github.com/BrainBlend-AI/atomic-agents) and [Instructor](https://github.com/instructor-ai/instructor). Uses the power of [Pydantic](https://docs.pydantic.dev) for data and schema validation and serialization.

- compose Agents made of Functions
- a router uses an LLM to process complex 'composite' user prompts, and automatically route them to the best sequence of your agents
  - the router rewrites the user prompt, to best suit each agent
- generate via OpenAI or AWS Bedrock or groq

[url_repo]: https://github.com/mrseanryan/gpt-multi-atomic-agents
[url_semver_org]: https://semver.org/

[![MIT License][img_license]][url_license]
[![Supported Python Versions][img_pyversions]][url_pyversions]
[![gpt-multi-atomic-agents][img_version]][url_version]

[![PyPI Releases][img_pypi]][url_pypi]
[![PyPI - Downloads](https://img.shields.io/pypi/dm/gpt-multi-atomic-agents.svg)](https://pypi.org/project/gpt-multi-atomic-agents)

[img_license]: https://img.shields.io/badge/License-MIT-blue.svg
[url_license]: https://github.com/mrseanryan/gpt-multi-atomic-agents/blob/master/LICENSE

[url_version]: https://pypi.org/project/gpt-multi-atomic-agents/

[img_version]: https://img.shields.io/static/v1.svg?label=SemVer&message=gpt-multi-atomic-agents&color=blue
[url_version]: https://pypi.org/project/bumpver/

[img_pypi]: https://img.shields.io/badge/PyPI-wheels-green.svg
[url_pypi]: https://pypi.org/project/gpt-multi-atomic-agents/#files

[img_pyversions]: https://img.shields.io/pypi/pyversions/gpt-multi-atomic-agents.svg
[url_pyversions]: https://pypi.python.org/pypi/gpt-multi-atomic-agents

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/K3K73ALBJ)

## Introduction

An LLM based Agents Framework using an Agent Oriented Programming approach to orchestrate agents using a shared Function Calling language.

The framework is generic and allows agents to be defined in terms of a name, description, accepted input function calls, and allowed output function calls.

The agents communicate indirectly using a blackboard. The language is a composed of function calls: each agent specifies what functions it understands as input, and what function calls it is able to generate. In this way, the agents can understand each other's output.

A router takes the user prompt and selects the best sequence of the most suitable agents, to handle the user prompt.

The router rewrites the user prompt to suit each agent, which improves quality and avoids unwanted output.

Finally, the output is returned in the form of an ordered list of function calls.

When integrating, the client would implement the functions. The client executes the functions according to the results generated by this framework.

## Examples

### Sim Life world builder

This is a demo 'Sim Life' world builder.
It uses 3 agents (Creature Creature, Vegetation Creator, Relationship Creator) to process user prompts.
The agents are defined in terms of functions.
The output is a series of Function Calls which can be implemented by the client, to build the Sim Life world.

#### Function Defintions

The AddCreature function:

```python
function_add_creature = FunctionSpecSchema(
    agent_name=creature_agent_name,
    function_name="AddCreature",
    description="Adds a new creature to the world (not vegetation)",
    parameters=[
        ParameterSpec(name="creature_name", type=ParameterType.string),
        ParameterSpec(name="allowed_terrain", type=ParameterType.string, allowed_values=terrain_types),
        ParameterSpec(name="age", type=ParameterType.int),
        ParameterSpec(name="icon_name", type=ParameterType.string, allowed_values=creature_icons),
    ]
)
```

The AddCreatureRelationship function:

```python
function_add_relationship = FunctionSpecSchema(
    agent_name=relationship_agent_name,
    function_name="AddCreatureRelationship",
    description="Adds a new relationship between two creatures",
    parameters=[
        ParameterSpec(
            name="from_name", type=ParameterType.string
        ),
        ParameterSpec(
            name="to_name", type=ParameterType.string
        ),
        ParameterSpec(
            name="relationship_name",
            type=ParameterType.string,
            allowed_values=["eats", "buys", "feeds", "sells"],
        ),
    ],
)
```

#### Agent Definitions

The Creature Creator agent is defined in terms of:

- its description (a very short prompt)
- its input schema (a list of accepted function definitions)
- its output schema (a list of output function definitions)

Agents can exchange information indirectly, by reusing the same function defintions.

```python
def build_creature_agent():
    agent_definition = AgentDefinition(
        agent_name="Creature Creator",
        description="Creates new creatures given the user prompt. Ensures that ALL creatures mentioned by the user are created.",
        accepted_functions=[function_add_creature, function_add_relationship],
        input_schema=FunctionAgentInputSchema,
        initial_input=FunctionAgentInputSchema(
            functions_allowed_to_generate=[function_add_creature],
            previously_generated_functions=[]
        ),
        output_schema=FunctionAgentOutputSchema,
        topics=["creature"]
    )

    return agent_definition
```

Notes about this agent:
- this agent can only generate "AddCreature" function calls.
- the agent also accepts (understands) previous "AddCreature" calls, so that it knows what has already been created.
- additionally, this agent understands a subset of function calls from agents: here, it understands the "AddRelationship" function defined by `function_add_relationship`. See the [example source code](./examples/sim_life/main.py) folder for more details.

#### Using the Agents in a chat loop

The agents can be used together to form a chat bot:

```python
from gpt_multi_atomic_agents import functions_expert_service, config
from . import agents

def run_chat_loop(given_user_prompt: str|None = None) -> list:
    CHAT_AGENT_DESCRIPTION = "Handles users questions about an ecosystem game like Sim Life"

    agent_definitions = [
        build_creature_agent(), build_relationship_agent(), build_vegatation_agent()  # for more capabilities, add more agents here
    ]

    _config = config.Config(
        ai_platform = config.AI_PLATFORM_Enum.bedrock_anthropic,
        model = config.ANTHROPIC_MODEL,
        max_tokens = config.ANTHROPIC_MAX_TOKENS,
        is_debug = False
        )

    return functions_expert_service.run_chat_loop(agent_definitions=agent_definitions, chat_agent_description=CHAT_AGENT_DESCRIPTION, _config=_config, given_user_prompt=given_user_prompt)
```

> note: if `given_user_prompt` is not set, then `run_chat_loop()` will wait for user input from the keyboard

See the [example source code](./examples/sim_life/main.py) folder for more details.

#### Example Execution

USER INPUT:
```
Add a sheep that eats grass
```

OUTPUT:
```
Generated 3 function calls
[Agent: Creature Creator] AddCreature( creature_name=sheep, icon_name=sheep-icon, land_type=prairie, age=1 )
[Agent: Plant Creator] AddPlant( plant_name=grass, icon_name=grass-icon, land_type=prairie )
[Agent: Relationship Creator] AddCreatureRelationship( from_name=sheep, to_name=grass, relationship_name=eats )
```

Because the framework has a dynamic router, it can handle more complex 'composite' prompts, such as:

> Add a cow that eats grass. Add a human - the cow feeds the human. Add and alien that eats the human. The human also eats cows.

The router figures out which agents to use, what order to run them in, and what prompt to send to each agent.

Finally, the framework combines the resulting function calls together and returns them to the client.

![example run](./images/screenshot-example-run.png)

## Setup

0. Install Python 3.11 and [poetry](https://github.com/python-poetry/install.python-poetry.org)

1. Install dependencies.

```
poetry install
```

2. Get an Open AI key

3. Set environment variable with your Open AI key:

```
export OPENAI_API_KEY="xxx"
```

Add that to your shell initializing script (`~/.zprofile` or similar)

Load in current terminal:

```
source ~/.zprofile
```

## Usage

Test script:

```
./test.sh
```
