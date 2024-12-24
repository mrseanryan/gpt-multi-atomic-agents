import { PostsClient } from "../gpt_maa_client/postsClient.js";

import {
  AgentExecutionPlanSchema,
  FunctionAgentDefinitionMinimal,
  FunctionCallGenerateRequest,
  FunctionCallSchema,
} from "../gpt_maa_client/models/index.js";

import { FunctionCallBlackboardAccessor } from "./function_call_blackboard_accessor.js";
import {
  dumpJson,
  printDetail,
  printTimeTaken,
  printWarning,
  showSpinner,
  startTimer,
  stopSpinner,
} from "./utils_print.js";
import { IDictionary } from "./utils.js";

export const generate_mutations_from_function_calls = async (
  client: PostsClient,
  userPrompt: string,
  agentDefinitions: FunctionAgentDefinitionMinimal[],
  chatAgentDescription: string,
  existing_plan: AgentExecutionPlanSchema | undefined = undefined,
  user_data: FunctionCallSchema[] | null = null
): Promise<FunctionCallBlackboardAccessor | null> => {
  const blackboard = new FunctionCallBlackboardAccessor({
    format: "function_call",
    internalNewlyGeneratedFunctions: [],
    internalNewlyGeneratedMessages: [],
    internalPreviouslyGeneratedFunctions: [],
    internalPreviousMessages: [],
  });
  if (user_data) {
    blackboard.set_user_data(user_data);
  }
  return generate_mutations(
    client,
    userPrompt,
    agentDefinitions,
    chatAgentDescription,
    existing_plan,
    blackboard
  );
};

const _validateUserPromptWillOverridePlan = (
  userPrompt: string,
  existing_plan: AgentExecutionPlanSchema | undefined = undefined
): void => {
  if (existing_plan) {
    if (userPrompt.length > 0) {
      printDetail(`USER: ${userPrompt}`);
      printWarning(
        "Have Generation Plan BUT also have a User Prompt - the server will discard the Plan generate a new plan."
      );
    } else {
      printDetail(`Generating from the Generation Plan...`);
    }
  } else {
    printDetail(`USER: ${userPrompt}`);
    if (userPrompt.length === 0) {
      printWarning("User prompt is empty");
    }
    printDetail(
      `Generating from user prompt - the Server will create a new Generation Plan...`
    );
  }
};

const _fixUpAgentParameters = (
  existing_plan: AgentExecutionPlanSchema
): void => {
  // bug in kiota?
  // plan RESPONSE: (comes back ok) `"agent_parameters":{"furniture-kind":["outdoor"]}}`
  // but generate REQUEST: need 'agent_parameters' =>  `"agent_parameters": { additionalData: { {"furniture-kind":["outdoor"]}} }`
  existing_plan.recommendedAgents?.forEach((agent) => {
    if (agent.agentParameters) {
      const newParameters: { additionalData: IDictionary<any> } = {
        additionalData: {},
      };
      const oldParameters = agent.agentParameters as IDictionary<any>;
      const keysToFix = Object.keys(oldParameters).filter(
        (k) => k !== "additionalData"
      );
      if (keysToFix.length > 0) {
        printWarning(
          `Fixing up Agent '${agent.agentName}' Parameters '${keysToFix}': kiota bug? - plan response does not align with generate request.`
        );
      }
      keysToFix.forEach((p) => {
        newParameters.additionalData[p] = oldParameters[p];
      });
      agent.agentParameters = newParameters;
    }
  });
};

export const generate_mutations = async (
  client: PostsClient,
  userPrompt: string,
  agentDefinitions: FunctionAgentDefinitionMinimal[],
  chatAgentDescription: string,
  existing_plan: AgentExecutionPlanSchema | undefined = undefined,
  blackboardAccessor: FunctionCallBlackboardAccessor | null = null
): Promise<FunctionCallBlackboardAccessor | null> => {
  const timer = startTimer("generate_mutations");

  userPrompt = userPrompt.trim();
  _validateUserPromptWillOverridePlan(userPrompt, existing_plan);
  if (existing_plan) _fixUpAgentParameters(existing_plan);

  const function_call_generate_request: FunctionCallGenerateRequest = {
    agentDefinitions: agentDefinitions,
    blackboard: blackboardAccessor?.get_internal_blackboard(),
    chatAgentDescription: chatAgentDescription,
    executionPlan: existing_plan,
    userPrompt: userPrompt,
  };

  let spinner = showSpinner();
  const blackboard = await client.generate_function_calls.post(
    function_call_generate_request
  );
  stopSpinner(spinner);

  dumpJson(blackboard);

  printTimeTaken(timer);

  if (!blackboard) {
    return null;
  }
  return new FunctionCallBlackboardAccessor(blackboard);
};
