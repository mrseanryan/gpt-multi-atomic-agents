// Example 'household chores' TypeScript client composed of function-call generating Agents.
// - the Agents speak a language you define, in terms of function calls
// - Agents can be configured to understand a subset of each others output
// - Because the service uses a Blackboard, the agents are then able to collaborate together, since they understand a subset of one another's output.

import { FunctionAgentDefinitionMinimal, FunctionCallSchema, FunctionSpecSchema, ParameterSpec } from "../gpt_maa_client/models/index.js"
import { DefaultHandler, execute, FunctionRegistry, HandlerBase } from "./function_call_executor.js"
import { handleUserPrompt } from "./index.js"

// =================================================
// Define the Functions
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

const mowerOutputFunctions: FunctionSpecSchema[] = [
    mowLawnFunction, produceCutGrassFunction
]

const furnitureMoverOutputFunctions: FunctionSpecSchema[] = [
    {
        functionName: "MoveFurniture",
        description: "Move furniture so it is not in the way, and move back again when appropriate.",
        parameters: [areaParameter]
    }
]

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

// =================================================
// Define our Handlers so we can execute any generated Function Calls

const functionRegistry = new FunctionRegistry();


const handleMowLawn = (functionCall: FunctionCallSchema): void => {
    console.log("<mowing the lawn>")
    console.log(`  params:`, functionCall.parameters)
}

const handleProduceCutGrass = (functionCall: FunctionCallSchema): void => {
    console.log("<producing cut grass>")
    console.log(`  params:`, functionCall.parameters)
}

class LawnHandler extends HandlerBase
{
    constructor(registry: FunctionRegistry) {
        super(registry);
        this.registerFunction(mowLawnFunction.functionName!, fc => handleMowLawn(fc))
        this.registerFunction(produceCutGrassFunction.functionName!, fc => handleProduceCutGrass(fc))
    }

    protected nameImplementation(): string
    {
        return "Lawn Handler";
    }
}

// Create the handlers (they register themselves)
const defaultHandler = new DefaultHandler(functionRegistry, (functionCall: FunctionCallSchema) => {
    console.log(`[default handler] for function call: ${functionCall.functionName}`, functionCall.parameters)
})
const lawnHandler = new LawnHandler(functionRegistry);

// TODO add WasteHandler, FurnitureHandler

// =================================================
// Declare the Agents in terms of the shared Functions
const lawnMowerAgent: FunctionAgentDefinitionMinimal = {
    agentName: "Lawn Mower",
    description: "Knows how to mow lawns",
    acceptedFunctions: mowerOutputFunctions,
    functionsAllowedToGenerate: mowerOutputFunctions,
    topics: ["garden", "lawn", "grass"],
}

const furnitureMoverAgent: FunctionAgentDefinitionMinimal = {
    agentName: "Furniture Mover",
    description: "Knows how to move furniture to different parts of garden, and move in or out of garden",
    acceptedFunctions: [...furnitureMoverOutputFunctions, mowLawnFunction]  // The furniture mover can observe when the lawn-mower needs to access that area
    ,
    functionsAllowedToGenerate: furnitureMoverOutputFunctions,
    topics: ["furniture"],
}

const wasteDisposerAgent: FunctionAgentDefinitionMinimal = {
    agentName: "Waste Disposer",
    description: "Knows how to collect and dispose of waste",
    acceptedFunctions: [...wasteDisposerOutputFunctions, produceCutGrassFunction], // The waste disposer can observe when the lawn-mower has generated waste
    functionsAllowedToGenerate: wasteDisposerOutputFunctions,
    topics: ["waste", "dispose"],
}

const agentDefinitions: FunctionAgentDefinitionMinimal[] = [
    lawnMowerAgent, furnitureMoverAgent, wasteDisposerAgent
]

// =================================================
// Chat with the Agents
const chatAgentDescription = "Handles questions about household chores such as garden, garden furniture and waste maintenance.";

await handleUserPrompt("What can you do?", agentDefinitions, chatAgentDescription)
const blackboardAccessor = await handleUserPrompt("Mow the lawn, dealing with any lawn furniture and waste. After mowing make sure waste is disposed of.", agentDefinitions, chatAgentDescription)

if (!blackboardAccessor) {
    throw new Error("No blackboard accessor was returned!")
}

// =================================================
// Display the messages from the Agents
const messages = blackboardAccessor.get_new_messages();
console.log(messages);

// =================================================
// Execute the Function Calls using our Handlers
blackboardAccessor.get_new_functions()
const onExecuteStart = async () => {
    console.log("(execution started)")
}
const onExecuteEnd = async () => {
    console.log("(execution ended)")
}
await execute(blackboardAccessor.get_new_functions(), functionRegistry, onExecuteStart, onExecuteEnd);
