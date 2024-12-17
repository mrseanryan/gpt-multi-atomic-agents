// Example 'household chores' TypeScript client composed of function-call generating Agents.
// - the Agents speak a language you define, in terms of function calls
// - Agents can be configured to understand a subset of each others output
// - Because the service uses a Blackboard, the agents are then able to collaborate together, since they understand a subset of one another's output.

import { execute } from "./function_call_executor.js";
import { handleUserPrompt } from "./index.js";
import {
  agentDefinitions,
  chatAgentDescription,
  functionRegistry,
} from "./resources_test_domain.js";
import { dumpJson, print, printDetail } from "./utils_print.js";

// =================================================
// Chat with the Agents

await handleUserPrompt(
  "What can you do?",
  agentDefinitions,
  chatAgentDescription
);
const blackboardAccessor = await handleUserPrompt(
  "mow lawn and clear waste. before that, move furniture away, and at the end, restore the furniture.",
  agentDefinitions,
  chatAgentDescription
);

if (!blackboardAccessor) {
  throw new Error("No blackboard accessor was returned!");
}

// =================================================
// Display the messages from the Agents
const messages = blackboardAccessor.get_new_messages();
dumpJson(messages);

// =================================================
// Execute the Function Calls using our Handlers
blackboardAccessor.get_new_functions();
const onExecuteStart = async (): Promise<boolean> => {
  printDetail("(execution started)");
  return true;
};
const onExecuteEnd = async () => {
  printDetail("(execution ended)");
};
await execute(
  blackboardAccessor.get_new_functions(),
  functionRegistry,
  onExecuteStart,
  onExecuteEnd
);
