import { FunctionAgentDefinitionMinimal } from "../gpt_maa_client/models/index.js";
import { FunctionCallBlackboardAccessor } from "./function_call_blackboard_accessor.js";
import { ExecutionError } from "./function_call_executor.js";
import { functionRegistry } from "./resources_test_domain.js";
import {
  dumpJsonAlways,
  printAssistant,
  printDetail,
  printError,
} from "./utils_print.js";
import { PostsClient } from "../gpt_maa_client/postsClient.js";
import {
  check_user_prompt,
  CommandAction,
  print_help,
} from "./repl_commands.js";
import { loadCustomAgents } from "./function_call_agent_stores.js";
import { createClient } from "./kiota_client.js";
import {
  load_blackboard_from_file,
  save_blackboard_to_file,
} from "./function_call_serde.js";
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

export const chatWithAgentsRepl = async (
  agentDefinitions: FunctionAgentDefinitionMinimal[],
  chatAgentDescription: string,
  baseurl: string,
  onExecuteStart: () => Promise<void>,
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

    const action = check_user_prompt(userPrompt, context.blackboardAccessor); // TODO xxx pass context: ICommandContext, then can move code down into cmds
    switch (action) {
      case CommandAction.handled_already:
        continue;
      case CommandAction.list_agents: {
        const customAgentSummaries = context.customAgents.map((a) => {
          return {
            agentName: a.agentName!,
            description: a.description!,
            source: "custom",
          };
        });
        const hardCodedAgentSummaries = context.agentDefinitions.map((a) => {
          return {
            agentName: a.agentName!,
            description: a.description!,
            source: "hard-coded",
          };
        });
        dumpJsonAlways(customAgentSummaries.concat(hardCodedAgentSummaries));
        continue;
      }
      case CommandAction.load_blackboard:
        {
          const filename = await readInputFromUser("Please enter a filename:");
          if (!filename) {
            printError("A filename is required in order to load");
            continue;
          }
          const newBlackboard = load_blackboard_from_file(filename);
          if (newBlackboard) {
            context.blackboardAccessor = newBlackboard;
            printDetail("(Blackboard loaded)");
          }
        }
        continue;
      case CommandAction.quit:
        printAssistant("Good bye!");
        return null;
      case CommandAction.reload_agents: {
        context.customAgents = loadCustomAgents();
        continue;
      }
      case CommandAction.save_blackboard:
        {
          if (!context.blackboardAccessor) {
            printError("No blackboard to save");
            continue;
          }
          const filename = await readInputFromUser("Please enter a filename:");
          if (!filename) {
            printError("A filename is required in order to save");
            continue;
          }
          save_blackboard_to_file(context.blackboardAccessor, filename);
        }
        continue;
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
