// Example 'household chores' TypeScript client composed of function-call generating Agents.
// - the Agents speak a language you define, in terms of function calls
// - Agents can be configured to understand a subset of each others output
// - Because the service uses a Blackboard, the agents are then able to collaborate together, since they understand a subset of one another's output.

import { FunctionCallBlackboardAccessor } from "./function_call_blackboard_accessor.js";
import {
  execute,
  ExecuteStartResult,
  ExecutionError,
} from "./function_call_executor.js";
import { handleUserPrompt } from "./index.js";
import {
  agentDefinitions,
  chatAgentDescription,
  functionRegistry,
} from "./resources_test_domain.js";
import { dumpJson, printDetail, printError } from "./utils_print.js";

// =================================================
// Chat with the Agents

await handleUserPrompt(
  "What can you do?",
  agentDefinitions,
  chatAgentDescription
);
const blackboardAccessor = await handleUserPrompt(
  "mow lawn of all areas and clear waste. before that, move furniture away, and at the end, restore the furniture.",
  agentDefinitions,
  chatAgentDescription
);

if (!blackboardAccessor) {
  throw new Error("No blackboard accessor was returned!");
}

// =================================================
// Display the messages from the Agents
const messages = blackboardAccessor.get_new_messages();
dumpJson(messages, "blackboard new messages");

// =================================================
// Execute the Function Calls using our Handlers
printDetail(`Executing the generated Function Calls (using Handlers)...`);
blackboardAccessor.get_new_functions();
const onExecuteStart = async (): Promise<ExecuteStartResult> => {
  printDetail("(execution started)");
  return {
    isOkToContinue: true,
    alsoExecutePreviousFunctions: false,
  };
};
const onExecuteEnd = async (
  errors: ExecutionError[],
  blackboardAccessor: FunctionCallBlackboardAccessor
) => {
  console.log("(execution ended)");
  if (errors.length) {
    printError(errors);
  }

  const new_user_data = blackboardAccessor.get_previously_generated_functions();
  blackboardAccessor.set_user_data(new_user_data);
};
await execute(
  functionRegistry,
  blackboardAccessor,
  onExecuteStart,
  onExecuteEnd
);
