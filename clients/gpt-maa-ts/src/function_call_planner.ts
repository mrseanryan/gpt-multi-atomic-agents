import { PostsClient } from "../gpt_maa_client/postsClient.js";

import {
  AgentDescription,
  AgentExecutionPlanSchema,
  FunctionAgentDefinitionMinimal,
  GeneratePlanRequest,
  Message,
} from "../gpt_maa_client/models/index.js";
import {
  dumpJson,
  printDetail,
  printTimeTaken,
  showSpinner,
  startTimer,
  stopSpinner,
} from "./utils_print.js";

const convertAgentDefinitionToDescription = (
  agentDefinition: FunctionAgentDefinitionMinimal
): AgentDescription => {
  let agentParameterNames: string[] = [];

  if (agentDefinition.agentParameters) {
    agentParameterNames = Object.keys(agentDefinition.agentParameters);
  }

  return {
    agentName: agentDefinition.agentName,
    description: agentDefinition.description,
    topics: agentDefinition.topics,
    agentParameterNames: agentParameterNames,
  };
};

export const generate_plan = async (
  client: PostsClient,
  userPrompt: string,
  agentDefinitions: FunctionAgentDefinitionMinimal[],
  chatAgentDescription: string,
  previousPlan: AgentExecutionPlanSchema | undefined = undefined,
  messages: Message[] | null = null
): Promise<AgentExecutionPlanSchema | undefined> => {
  const start = startTimer("generate_plan");
  const agentDescriptions: AgentDescription[] = agentDefinitions.map(
    convertAgentDefinitionToDescription
  );

  const generate_plan_request: GeneratePlanRequest = {
    agentDescriptions: agentDescriptions,
    chatAgentDescription: chatAgentDescription,
    previousPlan: previousPlan,
    userPrompt: userPrompt,
    messages: messages,
  };
  printDetail(`Generating a plan for user prompt '${userPrompt}'`);
  let spinner = showSpinner();
  const executionPlan = await client.generate_plan.post(generate_plan_request);
  stopSpinner(spinner);
  dumpJson(executionPlan);

  printTimeTaken(start);
  return executionPlan;
};
