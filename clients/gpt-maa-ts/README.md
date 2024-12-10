# gpt-maa-ts README (gpt-multi-atomic-agents - TypeScript Client)

A TypeScript client for submitting AgentDefinitions and user prompts to a gpt-multi-atomic-agents REST API, to generate supported mutations (function calls).

This client provides a mini framework for defining the Agents and handling the response.

This provides a clean approach to LLM based Agent calling, so the client can focus on the 'domain' or business logic:

- submit data in the form of Function Calls
- process the generated mutations, updating the application data

## Example

Agents are declared in terms of input and output functions.

First, we define the functions:

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

We also need to provide Handlers, to be able to execute the generated function calls. This is the main point of integration:

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
    console.log(`[default handler] for function call: ${functionCall.functionName}(${functionCall.parameters!.additionalData})`)
})
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

## Mainenance

To update the client, if the REST API has changed:

1. Copy the OpenAPI JSON from the Swagger site and paste into `gpt-maa-0.6.0.json`
2. Edit the JSON to be OpenAPI Version 3.0.0 (not 3.1.1):
    - see the existing files for differences
    - set `openapi` version to `"3.0.0"`
    - change `examples` -> `example`
    - [add `servers` section]
    - replace `"type": "null"` with `"nullable": true`

3. Run kyoto to generate the TypeScript client
```
./ update-from-openapi.sh
```
4. Run the test - update code as needed:

```
./test.sh
```

- tip: to test kiota in isolation, then run `./test.kiota.sh`

# References

- The REST client code is auto-generated via [kiota](https://learn.microsoft.com/en-us/openapi/kiota/quickstarts/typescript)
