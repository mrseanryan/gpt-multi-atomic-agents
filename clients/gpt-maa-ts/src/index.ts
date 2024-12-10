// A mini TypeScript framework to support defining Agents and executing them to generate Function Calls.
// - the Agents speak a language you define, in terms of function calls
// - Agents can be configured to understand a subset of each others output
// - Because the service uses a Blackboard, the agents are then able to collaborate together, since they understand a subset of one another's output.

import { FunctionAgentDefinitionMinimal, FunctionCallBlackboardOutput } from "../gpt_maa_client/models/index.js";
import { PostsClient } from "../gpt_maa_client/postsClient.js";
import { FunctionCallBlackboardAccessor } from "./function_call_blackboard_accessor.js";
import { generate_mutations } from "./function_call_generator.js";
import { generate_plan } from "./function_call_planner.js";
import { createClient } from "./kioto_client.js";

export { generate_mutations, generate_plan };
export * from "./function_call_executor.js";

export const handleUserPrompt = async (userPrompt: string, agentDefinitions: FunctionAgentDefinitionMinimal[], chatAgentDescription: string, baseurl: string|null= null): Promise<FunctionCallBlackboardAccessor|null> => {
    const client: PostsClient = createClient(baseurl)

    console.log(`USER: ${userPrompt}`)

    const executionPlan = await generate_plan(client, userPrompt, agentDefinitions, chatAgentDescription)

    console.log(`Executing the plan`)
    const blackboardAccessor = await generate_mutations(client, userPrompt, agentDefinitions, chatAgentDescription, executionPlan)

    return blackboardAccessor;
}
