// Example 'household chores' TypeScript client composed of function-call generating Agents.
// - the Agents speak a language you define, in terms of function calls
// - Agents can be configured to understand a subset of each others output
// - Because the service uses a Blackboard, the agents are then able to collaborate together, since they understand a subset of one another's output.

import { FunctionAgentDefinitionMinimal, FunctionSpecSchema, ParameterSpec } from "../gpt_maa_client/models/index.js"
import { handleUserPrompt } from "./function_call_generator.js"

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

// Declare the Agents
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

// Chat with the Agents
const chatAgentDescription = "Handles questions about household chores such as garden, garden furniture and waste maintenance.";

await handleUserPrompt("What can you do?", agentDefinitions, chatAgentDescription)
await handleUserPrompt("Mow the lawn, dealing with any lawn furniture and waste. After mowing make sure waste is disposed of.", agentDefinitions, chatAgentDescription)
