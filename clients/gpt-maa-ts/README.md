# gpt-maa-ts README (gpt-multi-atomic-agents - TypeScript Client)

A TypeScript client for submitting AgentDefinitions and user prompts to a gpt-multi-atomic-agents REST API, to generate supported mutations (function calls).

This client provides a mini framework for defining the Agents and handling the response.

This provides a clean approach to LLM based Agent calling, so the client can focus on the 'domain' or business logic:

- submit data in the form of Function Calls
- process the generated mutations, updating the application data

[npm package](https://www.npmjs.com/package/gpt-maa-ts)

## Example

As an Example, consider the domain of household maintenance agents which operate a Lawn Mower robot and a Waste Disposer robot.

There is one agent for mowing the lawn (the 'Lawn Mower' agent), and another agent for disposing of waste (the 'Waster Disposer' agent).

By collaborating together, the agents can complete the greater task of clearing and mowing the lawn, and then cleaning up afterwards.

Agents are declared in terms of input and output functions.

First, we define the functions which the Lawn Mower agent will use:

```TypeScript
const areaParameter: ParameterSpec = {
    name: "area",
    type: "string",
    allowedValues: ["front", "back"],
}

const mowLawnFunction: FunctionSpecSchema = {
    functionName: "MowLawn",
    description: "Mow the lawn and tidy it up",
    parameters: [areaParameter]
}
const produceCutGrassFunction: FunctionSpecSchema = {
    functionName: "ProduceCutGrass",
    description: "Produce cut grass waster",
    parameters: [areaParameter]
}
```

Next, we can define the Lawn Mower Agent in terms of Functions (as inputs and outputs):

```TypeScript
const lawnMowerAgent: FunctionAgentDefinitionMinimal = {
    agentName: "Lawn Mower",
    description: "Knows how to mow lawns",
    acceptedFunctions: [mowLawnFunction, produceCutGrassFunction],
    functionsAllowedToGenerate: [mowLawnFunction, produceCutGrassFunction],
    topics: ["garden", "lawn", "grass"],
}
```

> **_NOTE:_** Notice than an agent is basically a JSON document, so it can be imported, exported and even edited between REST API calls.

Next we define Functions that are specific to the Waste Disposer agent:

```TypeScript
const wasteDisposerOutputFunctions: FunctionSpecSchema[] = [
    {
        functionName: "CollectWaste",
        description: "Collect waste from an area",
        parameters: [areaParameter]
    },
    {
        functionName: "TakeWasteToCollectionSite",
        description: "Take previously collected waste from an area, to a collection site",
        parameters: [areaParameter, {
            name: "site_name",
            type: "string"
        }]
    }
]
```

Now that we have the waster disposer functions, and the waste output function of the Lawn Mower, we can define the Waste Disposer agent.

```TypeScript
const wasteDisposerAgent: FunctionAgentDefinitionMinimal = {
    agentName: "Waste Disposer",
    description: "Knows how to collect and dispose of waste",
    acceptedFunctions: [...wasteDisposerOutputFunctions, produceCutGrassFunction], // The waste disposer can observe when the lawn-mower has generated waste
    functionsAllowedToGenerate: wasteDisposerOutputFunctions,
    topics: ["waste", "dispose"],
}
```

Notice that the Waste Disposer agent takes the `produceCutGrassFunction` function as in an input. This allows the Waste Disposer agent to see and understand that part of the output from the Lawn Mower agent.

> **_NOTE:_** By sharing a subset of Function Calls, agents are able to understand each other's output, and collaborate indirectly via the REST API (internally, the REST API uses a Blackboard).

Finally, we also need to provide Handlers, to be able to execute the generated function calls.

> **_NOTE:_** Handlers are the main point of integration with the greater application. Handlers are 'fixed' since they are necessarily hard-coded against the greater application, whereas Agents are more dynamic.

```TypeScript
const functionRegistry = new FunctionRegistry();

class LawnHandler extends AreaHandlerBase
{
    constructor(registry: FunctionRegistry) {
        super(registry);
        this.registerFunction(mowLawnFunction.functionName!, this.handleMowLawn)
        this.registerFunction(produceCutGrassFunction.functionName!, this.handleProduceCutGrass)
    }

    private handleMowLawn(functionCall: FunctionCallSchema): void {
        console.log("<mowing the lawn>")
        console.log(`  params:`, functionCall.parameters)
    }

    private handleProduceCutGrass(functionCall: FunctionCallSchema): void {
        console.log("<producing cut grass>")
        console.log(`  params:`, functionCall.parameters)
    }

    protected nameImplementation(): string
    {
        return "Lawn Handler";
    }
}

// Create the handlers (they register themselves)
const defaultHandler = new DefaultAreaHandler(functionRegistry, (functionCall: FunctionCallSchema) => {
    console.log(`[default handler] for function call: ${functionCall.functionName}`, functionCall.parameters);
});
const lawnHandler = new LawnHandler(functionRegistry);
const wasteHandler = defaultHandler; // We can later add specific handling for Waste functions.
```

Now, we can use the agents to generate function calls, and execute them:

```TypeScript
const agentDefinitions: FunctionAgentDefinitionMinimal[] = [
    lawnMowerAgent, wasteDisposerAgent
]

// =================================================
// Chat with the Agents
const chatAgentDescription = "Handles questions about household chores such as garden, garden furniture and waste maintenance.";

const blackboardAccessor = await handleUserPrompt("Mow the lawn, dealing with any lawn furniture and waste. After mowing make sure waste is disposed of.", agentDefinitions, chatAgentDescription)

// =================================================
// Display the messages from the Agents
console.log(blackboardAccessor.get_new_messages());

// =================================================
// Execute the Function Calls using our Handlers
blackboardAccessor.get_new_functions()
const onExecuteStart = () => {
    console.log("(execution started)")
}
const onExecuteEnd = () => {
    console.log("(execution ended)")
}
execute(blackboardAccessor.get_new_functions(), functionRegistry, onExecuteStart, onExecuteEnd);
```

> **_NOTE:_** The Blackboard is serialized back to the client, in order to avoid making the server statefull. If that produces heavy network traffic, then future versions of the server may allow for state-full operation (however this comes with tradeoffs).

For more details, see [TypeScript Example Agents](https://github.com/mrseanryan/gpt-multi-atomic-agents/tree/master/clients/gpt-maa-ts/src/test_gpt_maa_client.ts).

# Setup

Install the depdencencies:

- [Node](https://nodejs.org/en/download/package-manager) v20.18+
- (for contributing) [Kiota](https://learn.microsoft.com/en-us/openapi/kiota/install?tabs=bash)

> **_NOTE:_** You need to add the kioto install location to your system path environment variable

```
./install.sh
```

> **_NOTE:_** You need to have the [gpt-multi-atomic-agents](https://github.com/mrseanryan/gpt-multi-atomic-agents) REST API running.

# Usage

For examples, see the [TypeScript Example Agents](https://github.com/mrseanryan/gpt-multi-atomic-agents/tree/master/clients/gpt-maa-ts/src/test_gpt_maa_client.ts).

# Test

```
./test.sh
```
