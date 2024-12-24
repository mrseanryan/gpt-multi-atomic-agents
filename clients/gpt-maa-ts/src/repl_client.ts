import { FunctionAgentDefinitionMinimal } from "../gpt_maa_client/models/index.js";
import { FunctionCallBlackboardAccessor } from "./function_call_blackboard_accessor.js";
import {
  ExecuteStartResult,
  ExecutionError,
} from "./function_call_executor.js";
import { PostsClient } from "../gpt_maa_client/postsClient.js";
import {
  check_user_prompt,
  CommandAction,
  print_help,
} from "./repl_commands.js";
import { loadCustomAgents } from "./function_call_agent_stores.js";
import { createClient } from "./kiota_client.js";
import {
  ExecuteReplState,
  GenerateReplState,
  PlanReplState,
  ReplContext,
} from "./repl_state_machine.js";
import { readInputFromUser } from "./util_input.js";
import {
  handleExecuteStateResult,
  handleGenerateStateResult,
  handlePlanStateResult,
} from "./repl_state_handlers.js";
import { printAssistant } from "./utils_print.js";
import { FunctionRegistry } from "./function_call_execution_registry.js";

/**
 *
 * @param agentDefinitions - The available Agent Definitions to use to plan and generate.
 * @param chatAgentDescription - Describes the 'fallback' chat agent: if no suitable agents are recommended, this chat agent will be recommended, if the user's prompt is supported. The description should include the purpose and domain of this chat system.
 * @param functionRegistry - The function call registry, which maps function calls to handlers.
 * @param baseurl - The URL of the gpt-multi-atomic-agents server.
 * @param onExecuteStart - Called at the start of execution, allowing client to prepare. If this returns with isOkToContinue=false, then the execution is cancelled.
 * @param onExecuteEnd - Called at the end of execution, allowing client to do any final operations or clean up.
 *                       errors: Any errors that occured during execution.
 *                       blackboardAccessor: Normally, the client has applied all new mutations, and want to continue from that state:
 *                       -> The client needs to update the blackboard, marking all new functions as 'previous' ->  const new_user_data = context.blackboardAccessor.get_new_functions(); context.blackboardAccessor.set_user_data(new_user_data);
 *                       -> BUT for clients where execution is always on a 'fresh copy', then they would NOT want to mark new functions as 'previous' (so they can iterate over them again).
 *
 */
export const chatWithAgentsRepl = async (
  agentDefinitions: FunctionAgentDefinitionMinimal[],
  chatAgentDescription: string,
  functionRegistry: FunctionRegistry,
  baseurl: string,
  onExecuteStart: () => Promise<ExecuteStartResult>,
  onExecuteEnd: (
    errors: ExecutionError[],
    blackboardAccessor: FunctionCallBlackboardAccessor
  ) => Promise<void>
): Promise<void> => {
  print_help();
  const client: PostsClient = createClient(baseurl);

  const context = new ReplContext(
    client,
    chatAgentDescription,
    functionRegistry,
    agentDefinitions,
    loadCustomAgents()
  );
  context.setState(new PlanReplState());

  while (true) {
    // TODO: allow for skipping of user input: currently using a special prompt 'PROCEED'
    const userPrompt = context.previousPrompt ?? (await readInputFromUser(""));
    if (!userPrompt) continue;
    context.addPlanMessage({ role: "user", message: userPrompt });
    context.previousPrompt = null;

    const action = await check_user_prompt(userPrompt, context);
    switch (action) {
      case CommandAction.handled_already:
        continue;
      case CommandAction.quit:
        printAssistant("Good bye!");
        return;
      case CommandAction.no_action:
        break;
      default:
        throw new Error(`Not a recognised CommandAction: ${action}`);
    }

    // Ask context to handle the user prompt, with the current state:
    context.userPrompt = userPrompt;
    await context.request();

    // Now, process the result of the state execution, deciding on the next state.
    // note: Changing states is responsiblity of this client.
    if (context.getState() instanceof PlanReplState) {
      await handlePlanStateResult(context);
      continue;
    } else if (context.getState() instanceof GenerateReplState) {
      await handleGenerateStateResult(context, onExecuteStart, onExecuteEnd);
      continue;
    } else if (context.getState() instanceof ExecuteReplState) {
      await handleExecuteStateResult(context);
      continue;
    } else {
      throw new Error("Not a recognised state!");
    }
  }
};
