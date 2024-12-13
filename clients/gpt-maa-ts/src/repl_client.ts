import {
  AgentExecutionPlanSchema,
  FunctionAgentDefinitionMinimal,
} from "../gpt_maa_client/models/index.js";
import { FunctionCallBlackboardAccessor } from "./function_call_blackboard_accessor.js";
import { execute, ExecutionError } from "./function_call_executor.js";
import { createClient, generate_mutations, generate_plan } from "./index.js";
import { functionRegistry } from "./resources_test_domain.js";
import {
  askUserIfOk,
  dumpJson,
  isQuit,
  printAssistant,
  printMessages,
  readInputFromUser,
} from "./utils_print.js";
import { PostsClient } from "../gpt_maa_client/postsClient.js";

export const chatWithAgentsRepl = async (
  agentDefinitions: FunctionAgentDefinitionMinimal[],
  chatAgentDescription: string,
  baseurl: string,
  onExecuteStart: () => Promise<void>,
  onExecuteEnd: (errors: ExecutionError[]) => Promise<void>
): Promise<FunctionCallBlackboardAccessor | null> => {
  printAssistant("Hello, can may I help you?");
  const client: PostsClient = createClient(baseurl);

  let executionPlan: AgentExecutionPlanSchema | undefined = undefined;

  let previousPrompt: string | null = null;

  while (true) {
    const userPrompt = previousPrompt ?? (await readInputFromUser(""));
    if (!userPrompt) continue;

    // TODO: check for other commands, not just quitting - see repl_commands.py
    // Type in a question for the AI. If you are not sure what to type, then ask it a question like 'What can you do?'
    // To exit, use the quit command
    // Available commands:
    //   clear - Clear the blackboard, starting over. (alias: reset)
    //   dump - Dump the current blackboard state to the console (alias: show)
    //   help - Display help text
    //   list-agents - List the active agents
    //   reload-agents - reload the agents from disk
    //   load - Load a blackboard from the local data store (also list the files)
    //   save - Save the blackboard to the local data store
    //   quit - Exit the chat loop (alias: bye, exit, stop)
    //
    //   NEW to TS only:
    //   reload-agents - Reloads the agent definition files.
    if (isQuit(userPrompt)) {
      printAssistant("Goodbye!\n");
      return null;
    }
    previousPrompt = null;

    executionPlan = await generate_plan(
      client,
      userPrompt,
      agentDefinitions,
      chatAgentDescription,
      executionPlan
    );

    printAssistant(executionPlan?.chatMessage);

    if (isOnlyChat(executionPlan?.recommendedAgents)) continue;

    const doContinue = await askUserIfOk(
      "Would you like to go ahead with that plan?",
      {
        yes: "Go ahead",
        no: "Say if you would like to change something",
      }
    );
    if (!doContinue.yes) {
      previousPrompt = doContinue.message;
      continue;
    }

    const blackboardAccessor = await generate_mutations(
      client,
      userPrompt,
      agentDefinitions,
      chatAgentDescription,
      executionPlan
    );
    if (!blackboardAccessor) {
      throw new Error("No blackboard accessor was returned!");
    }

    // =================================================
    // Display the messages from the Agents
    const messages = blackboardAccessor.get_new_messages();
    printMessages(messages);

    const doCreateApp = await askUserIfOk(
      "Would you like to apply those changes now?",
      {
        yes: "Go ahead",
        no: "Say if you would like to change something",
      }
    );
    if (!doCreateApp.yes) {
      previousPrompt = doCreateApp.message;
      continue;
    }

    // =================================================
    // Execute the Function Calls using our Handlers
    printAssistant("Performing your requested tasks now...");
    dumpJson(blackboardAccessor.get_new_functions());
    await execute(
      blackboardAccessor.get_new_functions(),
      functionRegistry,
      onExecuteStart,
      onExecuteEnd
    );

    // The client needs to update the blackboard at this point. Assumption: all the functions have been executed by the client.
    const new_user_data = blackboardAccessor.get_new_functions();
    blackboardAccessor.set_user_data(new_user_data);

    printAssistant("Is there anything else I can help with?");
  }
};

function isOnlyChat(
  recommendedAgents: import("./index.js").RecommendedAgent[] | null | undefined
) {
  if (!recommendedAgents) {
    return true;
  }

  return (
    recommendedAgents.length === 1 && recommendedAgents[0].agentName == "chat"
  );
}
