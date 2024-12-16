// Example 'household chores' TypeScript client composed of function-call generating Agents.
// - the Agents speak a language you define, in terms of function calls
// - Agents can be configured to understand a subset of each others output
// - Because the service uses a Blackboard, the agents are then able to collaborate together, since they understand a subset of one another's output.

import { chatWithAgentsRepl } from "./repl_client.js";
import {
  agentDefinitions,
  chatAgentDescription,
  functionRegistry,
} from "./resources_test_domain.js";
import { getConfig } from "./util_config.js";

// =================================================
// Chat with the Agents
async function main(): Promise<void> {
  const onExecuteStart = async () => {
    console.log("(execution started)");
  };
  const onExecuteEnd = async () => {
    console.log("(execution ended)");
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
