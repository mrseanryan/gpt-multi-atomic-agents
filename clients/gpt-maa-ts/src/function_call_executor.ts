import { FunctionCallSchema } from "../gpt_maa_client/models/index.js";
import { FunctionCallBlackboardAccessor } from "./function_call_blackboard_accessor.js";
import { FunctionRegistry } from "./function_call_execution_registry.js";
import {
  dumpJson,
  print,
  printDetail,
  printTimeTaken,
  showSpinner,
  startTimer,
  stopSpinner,
} from "./utils_print.js";

export interface ExecutionError {
  functionCallName: string;
  error: string;
}

export interface ExecuteStartResult {
  isOkToContinue: boolean; // False if the execution should be cancelled.
  alsoExecutePreviousFunctions: boolean; // True for clients that are executing from a 'fresh start' each time. Normally false, since client would continue executing from its current state.
}

/**
 *
 * @param registry - The function call registry, which maps function calls to handlers.
 * @param blackboardAccessor - The accessor for the blackboard, to allow client decide how to update, after execution.
 * @param onExecuteStart - Called at the start of execution, allowing client to prepare. If this returns with isOkToContinue=false, then the execution is cancelled.
 * @param onExecuteEnd - Called at the end of execution, allowing client to do any final operations or clean up.
 *                       errors: Any errors that occured during execution.
 *                       blackboardAccessor: Normally, the client has applied all new mutations, and want to continue from that state:
 *                       -> The client needs to update the blackboard, marking all new functions as 'previous':
 *                          const new_user_data = blackboardAccessor.get_new_functions();
 *                          blackboardAccessor.set_user_data(new_user_data);
 *                       -> BUT for clients where execution is always on a 'fresh copy', then they would NOT want to mark new functions as 'previous' (so they can iterate over them again).
 * @returns
 */
export const execute = async (
  registry: FunctionRegistry,
  blackboardAccessor: FunctionCallBlackboardAccessor,
  onExecuteStart: () => Promise<ExecuteStartResult>,
  onExecuteEnd: (
    errors: ExecutionError[],
    blackboardAccessor: FunctionCallBlackboardAccessor
  ) => Promise<void>
): Promise<void> => {
  const timer = startTimer("execute");

  let spinner = showSpinner();
  const executeStartResult = await onExecuteStart();
  stopSpinner(spinner);

  if (!executeStartResult.isOkToContinue) {
    // allow client to cancel, since Execution can be expensive for some clients
    return;
  }

  const errors: ExecutionError[] = [];

  let functionsToExecute: FunctionCallSchema[] =
    blackboardAccessor.get_new_functions();
  if (
    executeStartResult.alsoExecutePreviousFunctions &&
    blackboardAccessor.get_internal_blackboard()
      .internalPreviouslyGeneratedFunctions
  ) {
    printDetail(
      "(executing previous functions (that include new functions), assuming a 'fresh start'"
    );
    functionsToExecute =
      blackboardAccessor.get_internal_blackboard()
        .internalPreviouslyGeneratedFunctions!;
  }

  dumpJson(functionsToExecute, "functionsToExecute");
  functionsToExecute.forEach((call) => {
    try {
      if (!call.functionName) {
        errors.push({
          functionCallName: "<unknown>",
          error: "No function call name, so cannot identify a handler",
        });
        return;
      }

      const handler = registry.getHandler(call.functionName!);
      print(
        `Executing handler ${handler.name()} for function call ${
          call.functionName
        } from agent ${call.agentName}`
      );

      handler.HandleFunctionCall(call);
    } catch (e: any) {
      if (e instanceof Error) {
        errors.push({ functionCallName: call.functionName!, error: e.message });
      } else {
        errors.push({ functionCallName: call.functionName!, error: e });
      }
    }
  });

  spinner = showSpinner();
  await onExecuteEnd(errors, blackboardAccessor); // Pass the Blackboard accessor back to client, so they can decide how to update.

  stopSpinner(spinner);
  printTimeTaken(timer);
};
