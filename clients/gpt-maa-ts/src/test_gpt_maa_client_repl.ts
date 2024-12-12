// Example 'household chores' TypeScript client composed of function-call generating Agents.
// - the Agents speak a language you define, in terms of function calls
// - Agents can be configured to understand a subset of each others output
// - Because the service uses a Blackboard, the agents are then able to collaborate together, since they understand a subset of one another's output.

import { chatWithAgentsRepl } from "./repl_client.js";
import {
  agentDefinitions,
  chatAgentDescription,
} from "./resources_test_domain.js";

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
    "http://127.0.0.1:8000",
    onExecuteStart,
    onExecuteEnd
  ); // TODO make baseurl read from a config .env
}

main();
