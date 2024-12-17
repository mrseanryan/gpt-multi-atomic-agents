import { FunctionCallSchema } from "../gpt_maa_client/models/index.js";
import { FunctionRegistry } from "./function_call_execution_registry.js";
import {
  print,
  printTimeTaken,
  showSpinner,
  startTimer,
  stopSpinner,
} from "./utils_print.js";

export interface ExecutionError {
  functionCallName: string;
  error: string;
}

export const execute = async (
  functionCalls: FunctionCallSchema[],
  registry: FunctionRegistry,
  onExecuteStart: () => Promise<boolean>,
  onExecuteEnd: (errors: ExecutionError[]) => Promise<void>
): Promise<void> => {
  const timer = startTimer("execute");

  let spinner = showSpinner();
  const isOkToContinue = await onExecuteStart();
  stopSpinner(spinner);

  if (!isOkToContinue) {
    // allow client to cancel, since Execution can be expensive for some clients
    return;
  }

  const errors: ExecutionError[] = [];

  functionCalls.forEach((call) => {
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
  await onExecuteEnd(errors);
  stopSpinner(spinner);
  printTimeTaken(timer);
};
