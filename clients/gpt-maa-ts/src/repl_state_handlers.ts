// Handle the results of a State: this DOES involve changing States.

import {
  ExecuteStartResult,
  ExecutionError,
} from "./function_call_executor.js";
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
import { FunctionCallBlackboardAccessor } from "./function_call_blackboard_accessor.js";

const PROCEED_PROMPT = "proceed";

export const handlePlanStateResult = async (context: ReplContext) => {
  if (!context.executionPlan || !context.executionPlan.chatMessage) {
    printAssistant(
      "I am sorry, I could not quite understand that request. How else may I help you?"
    );
    return;
  }

  printAssistant(context.executionPlan.chatMessage);
  if (isOnlyChat(context.executionPlan.recommendedAgents)) {
    let chatRewrittenUserPrompt = "";
    if (context.executionPlan.recommendedAgents)
      chatRewrittenUserPrompt =
        context.executionPlan.recommendedAgents[0].rewrittenUserPrompt ??
        "<unknown>";
    printDetail(`(TODO: direct to Chat agent): ${chatRewrittenUserPrompt}`);
    return;
  } else {
    context.executionPlan.recommendedAgents?.forEach((ra) => {
      printDetail(`  DETAILS: ${ra.rewrittenUserPrompt}`);
    });

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
        return;
      }
      case "yes": {
        context.generateNeedsApproval = false;
        context.setState(new GenerateReplState());
        context.previousPrompt = PROCEED_PROMPT;
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
  onExecuteStart: () => Promise<ExecuteStartResult>,
  onExecuteEnd: (
    errors: ExecutionError[],
    blackboardAccessor: FunctionCallBlackboardAccessor
  ) => Promise<void>
) => {
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
      new ExecuteReplState(
        context.functionRegistry,
        onExecuteStart,
        onExecuteEnd
      )
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
          new ExecuteReplState(
            context.functionRegistry,
            onExecuteStart,
            onExecuteEnd
          )
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
