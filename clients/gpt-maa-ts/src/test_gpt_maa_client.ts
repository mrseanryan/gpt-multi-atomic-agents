import { AnonymousAuthenticationProvider } from "@microsoft/kiota-abstractions";
import { FetchRequestAdapter, HeadersInspectionHandler, KiotaClientFactory, ParametersNameDecodingHandler, RedirectHandler, RetryHandler, UserAgentHandler } from "@microsoft/kiota-http-fetchlibrary";
import { createPostsClient } from "../gpt_maa_client/postsClient.js";

import {AgentDescription, FunctionAgentDefinitionMinimal, FunctionCallGenerateRequest, FunctionSpecSchema, GeneratePlanRequest, ParameterSpec} from "../gpt_maa_client/models/index.js"

// API requires no authentication, so use the anonymous
// authentication provider
const authProvider = new AnonymousAuthenticationProvider();

// Create request adapter using the fetch-based implementation
//
// turn OFF compression as it breaks the fastapi server - see https://github.com/microsoft/kiota-typescript/issues/1439
const http = KiotaClientFactory.create(undefined, [
    new RetryHandler(), new RedirectHandler(), new ParametersNameDecodingHandler(), new UserAgentHandler(),  new HeadersInspectionHandler()
  ])
const adapter = new FetchRequestAdapter(authProvider, undefined, undefined, http);

// TODO configure adapter.baseUrl

// Create the API client
const client = createPostsClient(adapter);

// TODO extract agents_diy.ts

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

const lawnMowerAgent: FunctionAgentDefinitionMinimal = {
    agentName: "Lawn Mower",
    description: "Knows how to mow lawns",
    acceptedFunctions: mowerOutputFunctions,
    functionsAllowedToGenerate: mowerOutputFunctions,
    topics: ["garden", "lawn", "grass"],
}

const furnitureMoverOutputFunctions: FunctionSpecSchema[] = [
    {
        functionName: "MoveFurniture",
        description: "Move furniture so it is not in the way, and move back again when appropriate.",
        parameters: [areaParameter]
    }
]

const furnitureMoverAgent: FunctionAgentDefinitionMinimal = {
    agentName: "Furniture Mover",
    description: "Knows how to move furniture to different parts of garden, and move in or out of garden",
    acceptedFunctions: [...furnitureMoverOutputFunctions, mowLawnFunction]  // The furniture mover can observe when the lawn-mower needs to access that area
    ,
    functionsAllowedToGenerate: furnitureMoverOutputFunctions,
    topics: ["furniture"],
}

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

const convertAgentDefinitionToDescription = (agentDefinition: FunctionAgentDefinitionMinimal): AgentDescription => {
    return {
        agentName: agentDefinition.agentName,
        description: agentDefinition.description,
        topics: agentDefinition.topics,
        agentParameters: []  // TODO: ?? FunctionAgentDefinitionMinimal could have agentParameters: list[str]
    }
}

const agentDescriptions: AgentDescription[] = agentDefinitions.map(convertAgentDefinitionToDescription);

const chatAgentDescription = "Handles questions about household chores such as garden, garden furniture and waste maintenance.";

const dumnJson = (json: any) => {
    console.log(JSON.stringify(json))
}

const handleUserPrompt = async (userPrompt: string) => {
    console.log(`USER: ${userPrompt}`)
    const generate_plan_request: GeneratePlanRequest = {
        agentDescriptions: agentDescriptions,
        chatAgentDescription: chatAgentDescription,
        previousPlan: null,
        userPrompt: userPrompt
    }
    console.log(`Generating a plan for user prompt '${userPrompt}'`)
    const executionPlan = await client.generate_plan.post(generate_plan_request)
    dumnJson(executionPlan)

    console.log(`Executing the plan`)
    const function_call_generate_request: FunctionCallGenerateRequest = {
        agentDefinitions: agentDefinitions,
        blackboard: null,
        chatAgentDescription: chatAgentDescription,
        executionPlan: executionPlan,
        userPrompt: userPrompt
    }
    const blackboard = await client.generate_function_calls.post(function_call_generate_request)

    // TODO Make a FunctionCallBlackboardAccessor like the Python one
    dumnJson(JSON.stringify(blackboard))
}

await handleUserPrompt("What can you do?")
await handleUserPrompt("Mow the lawn, dealing with any lawn furniture and waste, before and after mowing.")

// TODO: bug - waster agent only gets used once (should also be used at the end)
