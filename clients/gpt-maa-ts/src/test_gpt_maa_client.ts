import { AnonymousAuthenticationProvider } from "@microsoft/kiota-abstractions";
import { FetchRequestAdapter, HeadersInspectionHandler, KiotaClientFactory, ParametersNameDecodingHandler, RedirectHandler, RetryHandler, UserAgentHandler } from "@microsoft/kiota-http-fetchlibrary";
import { createPostsClient } from "../gpt_maa_client/postsClient.js";

import {AgentDescription, GeneratePlanRequest} from "../gpt_maa_client/models/index.js"

// API requires no authentication, so use the anonymous
// authentication provider
const authProvider = new AnonymousAuthenticationProvider();
// Create request adapter using the fetch-based implementation

// turn OFF compression as it breaks the fastapi server - see https://github.com/microsoft/kiota-typescript/issues/1439
const http = KiotaClientFactory.create(undefined, [
    new RetryHandler(), new RedirectHandler(), new ParametersNameDecodingHandler(), new UserAgentHandler(),  new HeadersInspectionHandler()
  ])
const adapter = new FetchRequestAdapter(authProvider, undefined, undefined, http);

// TODO configure adapter.baseUrl

// Create the API client
const client = createPostsClient(adapter);

const userPrompt = "What can you do?";

const agentDescriptions: AgentDescription[] = [
 {
    agentName: "Garden Builder",
    description: "Knows how to build and maintain gardens and balconies",
    topics: ["garden"],
    agentParameters: []
 },
 {
    agentName: "Kitchen Builder",
    description: "Knows how to build and maintain kitchens",
    topics: ["kitchen"],
    agentParameters: []
 },
 {
    agentName: "Bathroom Builder",
    description: "Knows how to build and maintain bathrooms",
    topics: ["bathroom"],
    agentParameters: []
 },
]

const generate_plan_request: GeneratePlanRequest = {
    agentDescriptions: agentDescriptions,
    chatAgentDescription: "Handles questions about DIY",
    previousPlan: null,
    userPrompt: userPrompt
}
console.log(`Generating a plan for user prompt '${userPrompt}'`)

const plan = await client.generate_plan.post(generate_plan_request)
console.log(plan)
