// A mini TypeScript framework to support defining Agents and executing them to generate Function Calls.
// - the Agents speak a language you define, in terms of function calls
// - Agents can be configured to understand a subset of each others output
// - Because the service uses a Blackboard, the agents are then able to collaborate together, since they understand a subset of one another's output.

import { FunctionAgentDefinitionMinimal } from "../gpt_maa_client/models/index.js";
import { PostsClient } from "../gpt_maa_client/postsClient.js";
import { FunctionCallBlackboardAccessor } from "./function_call_blackboard_accessor.js";
import { generate_mutations } from "./function_call_generator.js";
import { generate_plan } from "./function_call_planner.js";
import { createClient } from "./kiota_client.js";
import { printAssistant, printDetail, printUser } from "./utils_print.js";

// Exports for consumers of this package
export { generate_mutations, generate_plan, createClient };
export * from "../gpt_maa_client/models/index.js";
export * from "./function_call_agent_stores.js";
export * from "./function_call_blackboard_accessor.js";
export * from "./function_call_execution_handlers.js";
export * from "./function_call_execution_registry.js";
export * from "./function_call_executor.js";
export * from "./function_call_generator.js";
export * from "./function_call_planner.js";
export * from "./function_call_serde.js";
export * from "./kiota_client.js";
export * from "./repl_client.js";
export * from "./repl_commands.js";
export * from "./repl_state_handlers.js";
export * from "./repl_state_machine.js";
export * from "./serializable_agent.js";
export * from "./util_config.js";
export * from "./util_file.js";
export * from "./utils.js";
export * from "./util_input.js";
export * from "./utils_print.js";

export const handleUserPrompt = async (
  userPrompt: string,
  agentDefinitions: FunctionAgentDefinitionMinimal[],
  chatAgentDescription: string,
  baseurl: string | null = null
): Promise<FunctionCallBlackboardAccessor | null> => {
  printUser(userPrompt);
  const client: PostsClient = createClient(baseurl);

  const executionPlan = await generate_plan(
    client,
    userPrompt,
    agentDefinitions,
    chatAgentDescription
  );

  printAssistant(executionPlan?.chatMessage);

  printDetail(`Executing the plan`);
  const blackboardAccessor = await generate_mutations(
    client,
    userPrompt,
    agentDefinitions,
    chatAgentDescription,
    executionPlan
  );

  return blackboardAccessor;
};
