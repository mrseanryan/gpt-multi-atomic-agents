// Example 'household chores' TypeScript client composed of function-call generating Agents.
// - the Agents speak a language you define, in terms of function calls
// - Agents can be configured to understand a subset of each others output
// - Because the service uses a Blackboard, the agents are then able to collaborate together, since they understand a subset of one another's output.

import { FunctionCallBlackboardAccessor } from "./function_call_blackboard_accessor.js";
import {
  ExecuteStartResult,
  ExecutionError,
} from "./function_call_executor.js";
import { chatWithAgentsRepl } from "./repl_client.js";
import {
  agentDefinitions,
  chatAgentDescription,
  functionRegistry,
} from "./resources_test_domain.js";
import { getConfig } from "./util_config.js";
import { printError } from "./utils_print.js";

// =================================================
// Chat with the Agents
async function main(): Promise<void> {
  const onExecuteStart = async (): Promise<ExecuteStartResult> => {
    console.log("(execution started)");
    return {
      isOkToContinue: true,
      alsoExecutePreviousFunctions: false,
    };
  };

  const onExecuteEnd = async (
    errors: ExecutionError[],
    blackboardAccessor: FunctionCallBlackboardAccessor
  ): Promise<void> => {
    console.log("(execution ended)");
    if (errors.length) {
      printError(errors);
    }

    // Assuming that client has applied all functions, and wants to continue from that state:
    const new_user_data = blackboardAccessor.get_new_functions();
    blackboardAccessor.set_user_data(new_user_data);
  };

  await chatWithAgentsRepl(
    agentDefinitions,
    chatAgentDescription,
    functionRegistry,
    getConfig().baseurl,
    onExecuteStart,
    onExecuteEnd
  );
}

main();
