import { PostsClient } from "../gpt_maa_client/postsClient.js";

import {AgentExecutionPlanSchema, FunctionAgentDefinitionMinimal, FunctionCallBlackboardOutput, FunctionCallGenerateRequest} from "../gpt_maa_client/models/index.js"

import { dumpJson } from "./kioto_client.js"
import { FunctionCallBlackboardAccessor } from "./function_call_blackboard_accessor.js";

export const generate_mutations = async (client: PostsClient, userPrompt: string, agentDefinitions: FunctionAgentDefinitionMinimal[], chatAgentDescription: string, existing_plan: AgentExecutionPlanSchema | undefined): Promise<FunctionCallBlackboardAccessor|null> => {
    console.log(`USER: ${userPrompt}`)

    console.log(`Executing the plan`)
    const function_call_generate_request: FunctionCallGenerateRequest = {
        agentDefinitions: agentDefinitions,
        blackboard: null,
        chatAgentDescription: chatAgentDescription,
        executionPlan: existing_plan,
        userPrompt: userPrompt
    }
    const blackboard = await client.generate_function_calls.post(function_call_generate_request)

    dumpJson(JSON.stringify(blackboard))

    // TODO Return a FunctionCallBlackboardAccessor like the Python one
    if (!blackboard) {
        return null;
    }
    return new FunctionCallBlackboardAccessor(blackboard);
}
