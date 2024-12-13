import {
  AgentExecutionPlanSchema,
  FunctionAgentDefinitionMinimal,
} from "../gpt_maa_client/models/index.js";
import { FunctionCallBlackboardAccessor } from "./function_call_blackboard_accessor.js";
import { execute, ExecutionError } from "./function_call_executor.js";
import { createClient, generate_mutations, generate_plan, load_blackboard_from_file, save_blackboard_to_file } from "./index.js";
import { functionRegistry } from "./resources_test_domain.js";
import {
  askUserIfOk,
  dumpJson,
  isQuit,
  printAssistant,
  printDetail,
  printError,
  printMessages,
  readInputFromUser,
} from "./utils_print.js";
import { PostsClient } from "../gpt_maa_client/postsClient.js";
import { check_user_prompt, CommandAction, print_help } from "./repl_commands.js";

export const chatWithAgentsRepl = async (
  agentDefinitions: FunctionAgentDefinitionMinimal[],
  chatAgentDescription: string,
  baseurl: string,
  onExecuteStart: () => Promise<void>,
  onExecuteEnd: (errors: ExecutionError[]) => Promise<void>
): Promise<FunctionCallBlackboardAccessor | null> => {
  print_help()
  const client: PostsClient = createClient(baseurl);

  let executionPlan: AgentExecutionPlanSchema | undefined = undefined;

  let previousPrompt: string | null = null;

  let blackboardAccessor: FunctionCallBlackboardAccessor | null = null;

  // TODO: refactor to a state machine
  while (true) {
    const userPrompt = previousPrompt ?? (await readInputFromUser(""));
    if (!userPrompt) continue;
    previousPrompt = null;

    // TODO: add more commands:
    //   list-agents - List the active agents
    //   reload-agents - reload the agent definition files.

    const action = check_user_prompt(userPrompt, blackboardAccessor)
    switch(action)
    {
        case CommandAction.quit:
            printAssistant("Good bye!")
            return null;
        case CommandAction.handled_already:
          continue
        case CommandAction.load_blackboard:
          {
              const filename = await readInputFromUser("Please enter a filename:")
              if (!filename)
              {
                  printError("A filename is required in order to load")
                  continue
              }
              const newBlackboard = load_blackboard_from_file(filename)
              if (newBlackboard)
              {
                  blackboardAccessor = newBlackboard
                  printDetail("(Blackboard loaded)")
              }
          }
          continue
        case CommandAction.save_blackboard:
            {
                if (!blackboardAccessor) {
                    printError("No blackboard to save")
                    continue
                }
                const filename = await readInputFromUser("Please enter a filename:")
                if (!filename)
                {
                    printError("A filename is required in order to save")
                    continue
                }
                save_blackboard_to_file(blackboardAccessor, filename)
            }
            continue
        case CommandAction.no_action:
            break
        default:
            throw new Error(`Not a recognised CommandAction: ${action}`)
        }

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

    blackboardAccessor = await generate_mutations(
      client,
      userPrompt,
      agentDefinitions,
      chatAgentDescription,
      executionPlan,
      blackboardAccessor
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

