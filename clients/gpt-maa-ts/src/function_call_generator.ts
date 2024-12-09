// A mini TypeScript framework to support defining Agents and executing them to generate Function Calls.
// - the Agents speak a language you define, in terms of function calls
// - Agents can be configured to understand a subset of each others output
// - Because the service uses a Blackboard, the agents are then able to collaborate together, since they understand a subset of one another's output.

import { AnonymousAuthenticationProvider } from "@microsoft/kiota-abstractions";
import { FetchRequestAdapter, HeadersInspectionHandler, KiotaClientFactory, ParametersNameDecodingHandler, RedirectHandler, RetryHandler, UserAgentHandler } from "@microsoft/kiota-http-fetchlibrary";
import { createPostsClient } from "../gpt_maa_client/postsClient.js";

import {AgentDescription, FunctionAgentDefinitionMinimal, FunctionCallGenerateRequest, GeneratePlanRequest} from "../gpt_maa_client/models/index.js"

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

const convertAgentDefinitionToDescription = (agentDefinition: FunctionAgentDefinitionMinimal): AgentDescription => {
    return {
        agentName: agentDefinition.agentName,
        description: agentDefinition.description,
        topics: agentDefinition.topics,
        agentParameters: []  // TODO: ?? FunctionAgentDefinitionMinimal could have agentParameters: list[str]
    }
}

const dumpJson = (json: any) => {
    console.log(JSON.stringify(json))
}

export const handleUserPrompt = async (userPrompt: string, agentDefinitions: FunctionAgentDefinitionMinimal[], chatAgentDescription: string) => {
    console.log(`USER: ${userPrompt}`)
    const agentDescriptions: AgentDescription[] = agentDefinitions.map(convertAgentDefinitionToDescription);

    const generate_plan_request: GeneratePlanRequest = {
        agentDescriptions: agentDescriptions,
        chatAgentDescription: chatAgentDescription,
        previousPlan: null,
        userPrompt: userPrompt
    }
    console.log(`Generating a plan for user prompt '${userPrompt}'`)
    const executionPlan = await client.generate_plan.post(generate_plan_request)
    dumpJson(executionPlan)

    console.log(`Executing the plan`)
    const function_call_generate_request: FunctionCallGenerateRequest = {
        agentDefinitions: agentDefinitions,
        blackboard: null,
        chatAgentDescription: chatAgentDescription,
        executionPlan: executionPlan,
        userPrompt: userPrompt
    }
    const blackboard = await client.generate_function_calls.post(function_call_generate_request)

    dumpJson(JSON.stringify(blackboard))

    // TODO Return a FunctionCallBlackboardAccessor like the Python one
}
