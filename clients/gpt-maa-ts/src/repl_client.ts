import { FunctionAgentDefinitionMinimal } from "../gpt_maa_client/models/index.js";
import { FunctionCallBlackboardAccessor } from "./function_call_blackboard_accessor.js";
import { ExecutionError } from "./function_call_executor.js";
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

export const chatWithAgentsRepl = async (
  agentDefinitions: FunctionAgentDefinitionMinimal[],
  chatAgentDescription: string,
  functionRegistry: FunctionRegistry,
  baseurl: string,
  onExecuteStart: () => Promise<boolean>,
  onExecuteEnd: (errors: ExecutionError[]) => Promise<void>
): Promise<FunctionCallBlackboardAccessor | null> => {
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
    context.previousPrompt = null;

    const action = await check_user_prompt(userPrompt, context);
    switch (action) {
      case CommandAction.handled_already:
        continue;
      case CommandAction.quit:
        printAssistant("Good bye!");
        return null;
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
