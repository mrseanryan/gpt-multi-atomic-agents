import {
  FunctionAgentDefinitionMinimal,
  Message,
} from "../gpt_maa_client/models/index.js";
import { loadCustomAgents } from "./function_call_agent_stores.js";
import { FunctionCallBlackboardAccessor } from "./function_call_blackboard_accessor.js";
import {
  list_blackboard_files,
  load_blackboard_from_file,
  save_blackboard_to_file,
} from "./function_call_serde.js";
import { SerializableAgentWithCategories } from "./serializable_agent.js";
import { isDebugActive, toggleIsDebugActive } from "./util_config.js";
import { readInputFromUser } from "./util_input.js";
import {
  dumpJson,
  dumpJsonAlways,
  print,
  printAssistant,
  printDetail,
  printError,
} from "./utils_print.js";

export enum CommandAction {
  no_action = "no_action",
  handled_already = "handled_already",
  quit = "quit",
}

export abstract class ReplCommandBase {
  public isDebugOnly = (): boolean => true;
  public abstract get_name(): string;
  public abstract get_description(): string;
  public abstract get_aliases(): string[];

  public async do(context: IReplCommandContext): Promise<CommandAction> {
    throw new Error("do() not implemented");
  }
}

abstract class UserVisibleReplCommandBase extends ReplCommandBase {
  public override isDebugOnly = (): boolean => false;
}

class ClearReplCommand extends ReplCommandBase {
  public get_name = () => "clear";

  public get_aliases = () => ["reset"];

  public get_description = () => "Clear the blackboard, starting over.";

  public async do(context: IReplCommandContext | null): Promise<CommandAction> {
    if (!context?.blackboardAccessor) return CommandAction.handled_already;

    context.blackboardAccessor._reset_all();
    printDetail("(Blackboard has been reset)");
    return CommandAction.handled_already;
  }
}

class DumpReplCommand extends ReplCommandBase {
  public get_name = () => "dump";

  public get_aliases = () => ["show"];

  public get_description = () =>
    "Dump the current blackboard state to the console";

  public async do(context: IReplCommandContext): Promise<CommandAction> {
    if (!context.blackboardAccessor) {
      printDetail("(no blackboard to dump)");
      return CommandAction.handled_already;
    }
    dumpJson(context.blackboardAccessor, "blackboardAccessor");
    dumpJson(context.getPlanMessages(), "plan messages");
    return CommandAction.handled_already;
  }
}

class ToggleDebugCommand extends UserVisibleReplCommandBase {
  public get_name = () => "toggle-debug";
  public get_aliases = () => ["td"];
  public get_description = () =>
    "Toggles debug mode on and off (in debug mode, more commands are available).";
  public async do(context: IReplCommandContext): Promise<CommandAction> {
    const isDebug = toggleIsDebugActive();
    print_help({ hideWelcome: true });
    printDetail(isDebug ? "<Debugging is ON>" : "<Debugging is OFF>");

    return CommandAction.handled_already;
  }
}

class HelpReplCommand extends UserVisibleReplCommandBase {
  public get_name = () => "help";
  public get_aliases = () => [];

  public get_description = () => "Display help text";

  public async do(context: IReplCommandContext): Promise<CommandAction> {
    print_help();
    return CommandAction.handled_already;
  }
}

class ListReplCommand extends ReplCommandBase {
  public get_name = () => "list";
  public get_aliases = () => [];

  public get_description = () =>
    "List the local data files from previous blackboards";

  public async do(context: IReplCommandContext): Promise<CommandAction> {
    list_blackboard_files(context.blackboardAccessor);
    return CommandAction.handled_already;
  }
}

class ListAgentsReplCommand extends ReplCommandBase {
  public get_name = () => "list-agents";
  public get_aliases = () => ["lag"];

  public get_description = () =>
    "List the active agents (both hard-coded agents and custom agents that were loaded from Agent Stores)";

  public async do(context: IReplCommandContext): Promise<CommandAction> {
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
    return CommandAction.handled_already;
  }
}

class LoadReplCommand extends ReplCommandBase {
  public get_name = () => "load";
  public get_aliases = () => [];

  public get_description = () => "Load a blackboard from the local data store";

  public do = async (context: IReplCommandContext): Promise<CommandAction> => {
    const filename = await readInputFromUser("Please enter a filename:");
    if (!filename) {
      printError("A filename is required in order to load");
      return CommandAction.handled_already;
    }
    const newBlackboard = load_blackboard_from_file(filename);
    if (newBlackboard) {
      context.blackboardAccessor = newBlackboard;
      printDetail("(Blackboard loaded)");
    }
    return CommandAction.handled_already;
  };
}

class ReloadAgentsReplCommand extends ReplCommandBase {
  public get_name = () => "reload-agents";
  public get_aliases = () => ["rag"];

  public get_description = () =>
    "Reload the custom agents from the Agent Stores";

  public async do(context: IReplCommandContext): Promise<CommandAction> {
    context.customAgents = loadCustomAgents();
    return CommandAction.handled_already;
  }
}

class SaveReplCommand extends ReplCommandBase {
  public get_name = () => "save";
  public get_aliases = () => [];

  public get_description = () => "Save the blackboard to the local data store";

  public async do(context: IReplCommandContext): Promise<CommandAction> {
    if (!context.blackboardAccessor) {
      printError("No blackboard to save");
      return CommandAction.handled_already;
    }
    const filename = await readInputFromUser("Please enter a filename:");
    if (!filename) {
      printError("A filename is required in order to save");
      return CommandAction.handled_already;
    }
    save_blackboard_to_file(context.blackboardAccessor, filename);
    return CommandAction.handled_already;
  }
}

class QuitReplCommand extends UserVisibleReplCommandBase {
  public get_name = () => "quit";

  public get_aliases = () => ["bye", "exit", "stop"];

  public get_description = () => "Exit the chat loop";

  public do = async (context: IReplCommandContext): Promise<CommandAction> =>
    CommandAction.quit;
}

const commands: ReplCommandBase[] = [
  new ClearReplCommand(),
  new DumpReplCommand(),
  new ToggleDebugCommand(),
  new HelpReplCommand(),
  new ListAgentsReplCommand(),
  new ListReplCommand(),
  new LoadReplCommand(),
  new ReloadAgentsReplCommand(),
  new SaveReplCommand(),
  new QuitReplCommand(),
];
const MIN_USER_PROMPT = 4;

const getActiveCommands = (): ReplCommandBase[] => {
  return commands
    .filter((c) => !c.isDebugOnly() || isDebugActive())
    .sort((a, b) => (a.get_name() > b.get_name() ? 0 : 1));
};

const _is_user_input_matching = (
  user_prompt: string,
  aliases: string[]
): boolean => aliases.includes(user_prompt.toLowerCase().trim());

export interface IReplCommandContext {
  blackboardAccessor: FunctionCallBlackboardAccessor | null;
  agentDefinitions: FunctionAgentDefinitionMinimal[];
  customAgents: SerializableAgentWithCategories[];
  getPlanMessages(): Message[];
}

export const check_user_prompt = async (
  user_prompt: string,
  context: IReplCommandContext
): Promise<CommandAction> => {
  user_prompt = user_prompt.trim();
  if (!user_prompt) {
    return await new HelpReplCommand().do(context);
  }

  const activeCommands = getActiveCommands();
  for (let i = 0; i < activeCommands.length; i++) {
    const command = activeCommands[i];
    const aliases = command.get_aliases().concat([command.get_name()]);
    if (_is_user_input_matching(user_prompt, aliases)) {
      return await command.do(context);
    }
  }

  // user prompt is suspiciously short:
  if (user_prompt.length < MIN_USER_PROMPT)
    return await new HelpReplCommand().do(context);

  return CommandAction.no_action;
};

export const print_help = (options?: { hideWelcome: boolean }): void => {
  if (!options?.hideWelcome) {
    printAssistant("Welcome to multi-agent chat");
    print(
      "Type in a question for the AI. If you are not sure what to type, then ask it a question like 'What can you do?'"
    );
    print("To exit, use the quit command");
  }

  print("Available commands:");
  const activeCommands = getActiveCommands();
  for (let i = 0; i < activeCommands.length; i++) {
    const command = activeCommands[i];
    const aliases = command.get_aliases().join(", ");

    let aliasesDescription = "";
    if (aliases.length) aliasesDescription = ` (alias: ${aliases})`;
    print(
      `  ${command.get_name()} - ${command.get_description()}${aliasesDescription}`
    );
  }
};
