# gpt-multi-atomic-agents
A simple dynamic multi-agent framework based on [atomic-agents](https://github.com/BrainBlend-AI/atomic-agents) and [Instructor](https://github.com/instructor-ai/instructor). Uses the power of [Pydantic](https://docs.pydantic.dev) for data and schema validation and serialization.

- compose Agents made of Functions
- a router uses an LLM to process complex 'composite' user prompts, and automatically route them to the best sequence of your agents
  - the router rerites the user prompt, to best suit each agent
- generate via OpenAI or AWS Bedrock or groq

## Introduction

This is an LLM based Agents Framework using an Agent Oriented Programming approach to orchestrate agents using a shared Function Calling language.

The framework is generic and allows agents to be defined in terms of a name, description, accepted input function calls, and allowed output function calls.

The agents communicate indirectly using a blackboard. The language is a composed of the function calls: each agent specifies what functions it understands as input, and what function calls it is able to generate. In this way, the agents can understand each other's output.

A router takes the user prompt and selects the best sequence of the most suitable agents, to handle the user prompt.
The router rewrites the user prompt to suit each agent, which improves quality and avoids unwanted output.

Finally, the output is returned in the form of an ordered list of function calls.

When integrating, the client would implement the functions. The client executes the functions according to the results from this framework.

## Examples

### SimLife world builder

This is a demo 'Sim Life' world builder.
It uses 3 agents (Creature Creature, Vegetation Creator, Relationship Creator) to process user prompts.
The output is a series of Function Calls which can be implemented by the client, to build the Sim Life world.

INPUT:
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

Becuase the framework has a dynamic router, it can handle more complex 'composite' prompts, such as:

- "Add a cow that eats grass. Add a human - the cow feeds the human. Add and alien that eats the human. The human also eats cows."

The router figures out which agents to use, what order to run them in, and what prompt to send to each agent.

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
