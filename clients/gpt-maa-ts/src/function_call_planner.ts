import { PostsClient } from "../gpt_maa_client/postsClient.js";

import {AgentDescription, AgentExecutionPlanSchema, FunctionAgentDefinitionMinimal, FunctionCallBlackboardOutput, FunctionCallGenerateRequest, GeneratePlanRequest} from "../gpt_maa_client/models/index.js"
import { dumpJson } from "./kioto_client.js";

const convertAgentDefinitionToDescription = (agentDefinition: FunctionAgentDefinitionMinimal): AgentDescription => {
    return {
        agentName: agentDefinition.agentName,
        description: agentDefinition.description,
        topics: agentDefinition.topics,
        agentParameters: []  // TODO: ?? FunctionAgentDefinitionMinimal could have agentParameters: list[str]
    }
}

export const generate_plan = async (client: PostsClient, userPrompt: string, agentDefinitions: FunctionAgentDefinitionMinimal[], chatAgentDescription: string): Promise<AgentExecutionPlanSchema | undefined> => {
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

    return executionPlan;
};
