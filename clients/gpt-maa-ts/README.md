# gpt-maa-ts README (gpt-multi-atomic-agents - TypeScript Client)

A TypeScript client for submitting AgentDefinitions and user prompts to a gpt-multi-atomic-agents REST API, to generate supported mutations (function calls).

This client provides a mini framework for defining the Agents and handling the response.

This provides a clean approach to LLM based Agent calling, so the client can focus on the 'domain' or business logic:

- submit data in the form of Function Calls
- process the generated mutations, updating the application data

[npm package](https://www.npmjs.com/package/gpt-maa-ts)

## Example

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

Notice that the Waste Disposer agent takes the `produceCutGrassFunction` function as in an input. This allows the Waste Disposer agent to see and understand that part of the output from the Lawn Mower agent.

> **_NOTE:_** By sharing a subset of Function Calls, agents are able to understand each other's output, and collaborate indirectly via the REST API (internall, the REST API uses a Blackboard).

```TypeScript
const wasteDisposerAgent: FunctionAgentDefinitionMinimal = {
    agentName: "Waste Disposer",
    description: "Knows how to collect and dispose of waste",
    acceptedFunctions: [...wasteDisposerOutputFunctions, produceCutGrassFunction], // The waste disposer can observe when the lawn-mower has generated waste
    functionsAllowedToGenerate: wasteDisposerOutputFunctions,
    topics: ["waste", "dispose"],
}
```

Finally, we also need to provide Handlers, to be able to execute the generated function calls.

> **_NOTE:_** Handlers are the main point of integration with the greater application.

```TypeScript
const functionRegistry = new FunctionRegistry();

class LawnHandler extends HandlerBase
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
const defaultHandler = new DefaultHandler(functionRegistry, (functionCall: FunctionCallSchema) => {
    console.log(`[default handler] for function call: ${functionCall.functionName}`, functionCall.parameters);
});
const lawnHandler = new LawnHandler(functionRegistry);
```

Next, we can define the Agents in terms of the Functions (as inputs and outputs):

```TypeScript
const lawnMowerAgent: FunctionAgentDefinitionMinimal = {
    agentName: "Lawn Mower",
    description: "Knows how to mow lawns",
    acceptedFunctions: mowerOutputFunctions,
    functionsAllowedToGenerate: mowerOutputFunctions,
    topics: ["garden", "lawn", "grass"],
}
```

Now, we can use the agents to generate function calls, and execute them:

```TypeScript
const agentDefinitions: FunctionAgentDefinitionMinimal[] = [
    lawnMowerAgent
]

// =================================================
// Chat with the Agents
const chatAgentDescription = "Handles questions about household chores such as garden, garden furniture and waste maintenance.";

const bbAccessor = await handleUserPrompt("Mow the lawn, dealing with any lawn furniture and waste. After mowing make sure waste is disposed of.", agentDefinitions, chatAgentDescription)

// =================================================
// Display the messages from the Agents
console.log(bbAccessor.get_new_messages());

// =================================================
// Execute the Function Calls using our Handlers
bbAccessor.get_new_functions()
const onExecuteStart = () => {
    console.log("(execution started)")
}
const onExecuteEnd = () => {
    console.log("(execution ended)")
}
execute(bbAccessor.get_new_functions(), functionRegistry, onExecuteStart, onExecuteEnd);
```

For more details, see [TypeScript Example Agents](https://github.com/mrseanryan/gpt-multi-atomic-agents/tree/master/clients/gpt-maa-ts/src/test_gpt_maa_client.ts).

# Setup

Install the depdencencies:

- [Node](https://nodejs.org/en/download/package-manager) v20.18+
- [Kiota](https://learn.microsoft.com/en-us/openapi/kiota/install?tabs=bash)

note: You need to add the kioto install location to your system path environment variable

```
./install.sh
```

# Usage

# Test

```
./test.sh
```
