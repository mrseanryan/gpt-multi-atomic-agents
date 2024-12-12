// Resource: an example of a 'household chores bots' domain.
import { FunctionAgentDefinitionMinimal, FunctionCallSchema, FunctionSpecSchema, ParameterSpec } from "../gpt_maa_client/models/index.js"
import { DefaultHandler, execute, FunctionRegistry, HandlerBase } from "./function_call_executor.js"
import { print, printDetail } from "./utils_print.js"

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

export const functionRegistry = new FunctionRegistry();


const handleMowLawn = (functionCall: FunctionCallSchema): void => {
    print("<mowing the lawn>")
    printDetail(`  params:`, functionCall.parameters)
}

const handleProduceCutGrass = (functionCall: FunctionCallSchema): void => {
    print("<producing cut grass>")
    printDetail(`  params:`, functionCall.parameters)
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
new DefaultHandler(functionRegistry, (functionCall: FunctionCallSchema) => {
    printDetail(`[default handler] for function call: ${functionCall.functionName}`, functionCall.parameters)
})
new LawnHandler(functionRegistry);

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

export const agentDefinitions: FunctionAgentDefinitionMinimal[] = [
    lawnMowerAgent, furnitureMoverAgent, wasteDisposerAgent
]

export const chatAgentDescription = "Handles questions about household chores such as garden, garden furniture and waste maintenance.";
