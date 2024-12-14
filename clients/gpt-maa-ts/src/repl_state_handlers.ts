import { ExecutionError } from "./function_call_executor.js";
import { functionRegistry } from "./resources_test_domain.js";
import {
  printAssistant,
  printDetail,
  printError,
  printMessages,
} from "./utils_print.js";
import {
  ExecuteReplState,
  GenerateReplState,
  PlanReplState,
  ReplContext,
} from "./repl_state_machine.js";
import { askUserWithOptions } from "./util_input.js";

const PROCEED_PROMPT = "proceed";

export const handlePlanStateResult = async (context: ReplContext) => {
  printAssistant(context.executionPlan?.chatMessage);
  if (isOnlyChat(context.executionPlan?.recommendedAgents)) {
    printDetail("(TODO: direct to Chat agent)");
    return;
  } else {
    const chosen = await askUserWithOptions({
      prompt: "Would you like to go ahead with that plan?",
      options: [
        {
          name: "yes, with approval",
          description: "Go ahead, but let me check the details",
          needsUserInput: false,
        },
        {
          name: "yes",
          description: "Go ahead, and take care of the details",
          needsUserInput: false,
        },
        {
          name: "no",
          description: "You want to change something",
          needsUserInput: true,
        },
      ],
    });
    switch (chosen.chosen.name) {
      case "no":
        context.previousPrompt = chosen.userInput;
        return;
      case "yes, with approval": {
        context.generateNeedsApproval = true;
        context.setState(new GenerateReplState());
        context.previousPrompt = PROCEED_PROMPT;
        // context.request();
        return;
      }
      case "yes": {
        context.generateNeedsApproval = false;
        context.setState(new GenerateReplState());
        context.previousPrompt = PROCEED_PROMPT;
        // context.request();
        return;
      }
      default: {
        printError("(not a recognised option");
        return;
      }
    }
  }
};

export const handleGenerateStateResult = async (
  context: ReplContext,
  onExecuteStart: () => Promise<void>,
  onExecuteEnd: (errors: ExecutionError[]) => Promise<void>
) => {
  // =================================================
  // Display the messages from the Agents
  if (!context.blackboardAccessor) {
    printError(
      "blackboardAccessor was not set by the Generate state - reverting to Plan state"
    );
    context.setState(new PlanReplState());
    return;
  }
  const messages = context.blackboardAccessor.get_new_messages();
  printMessages(messages);

  if (!context.generateNeedsApproval!) {
    context.setState(
      new ExecuteReplState(functionRegistry, onExecuteStart, onExecuteEnd)
    );
    context.previousPrompt = PROCEED_PROMPT;
    return;
  }

  {
    const chosen = await askUserWithOptions({
      prompt: "Would you like to apply those changes now?",
      options: [
        {
          name: "yes",
          description: "Go ahead, and take care of the details",
          needsUserInput: false,
        },
        {
          name: "no",
          description: "You want to change something",
          needsUserInput: true,
        },
        {
          name: "no - change plan",
          description: "You want to change the plan (start over)",
          needsUserInput: true,
        },
      ],
    });
    switch (chosen.chosen.name) {
      case "yes": {
        context.setState(
          new ExecuteReplState(functionRegistry, onExecuteStart, onExecuteEnd)
        );
        context.previousPrompt = PROCEED_PROMPT;
        return;
      }
      case "no": {
        context.previousPrompt = chosen.userInput;
        return;
      }
      case "no - change plan": {
        context.previousPrompt = chosen.userInput;
        context.setState(new PlanReplState());
        return;
      }
      default: {
        printError("(not a recognised option");
        return;
      }
    }
  }
};

export const handleExecuteStateResult = async (context: ReplContext) => {
  if (!context.blackboardAccessor) {
    throw new Error("Blackboard not set, even after generate");
  }

  // The client needs to update the blackboard at this point. Assumption: all the functions have been executed by the client.
  const new_user_data = context.blackboardAccessor.get_new_functions();
  context.blackboardAccessor.set_user_data(new_user_data);

  printAssistant("Is there anything else I can help with?");
  context.setState(new PlanReplState());
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
