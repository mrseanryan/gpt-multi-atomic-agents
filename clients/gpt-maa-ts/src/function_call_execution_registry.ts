import {
  FunctionCallSchema,
  FunctionSpecSchema,
} from "../gpt_maa_client/models/index.js";
import { IDictionary } from "./utils.js";
import { printWarning } from "./utils_print.js";

export interface IFunctionCallHandler {
  name(): string;
  HandleFunctionCall(functionCall: FunctionCallSchema): void;
}

export class FunctionRegistry {
  private defaultHandler: IFunctionCallHandler | null = null;
  private functionNameToHandler: IDictionary<IFunctionCallHandler> = {};
  private categoryToFunction: IDictionary<FunctionSpecSchema[]> = {};

  public registerDefaultHandler(handler: IFunctionCallHandler): void {
    if (this.defaultHandler) {
      throw new Error("A default handler is already registered");
    }

    this.defaultHandler = handler;
  }

  public registerHandler(
    fun: FunctionSpecSchema,
    category: string,
    handler: IFunctionCallHandler
  ): void {
    if (!fun.functionName) throw new Error("The function must have a name");

    if (this.functionNameToHandler[fun.functionName])
      throw new Error(
        `A handler is already registered for function ${fun.functionName}`
      );

    this.functionNameToHandler[fun.functionName] = handler;

    if (!Object.keys(this.categoryToFunction).includes(category)) {
      this.categoryToFunction[category] = [];
    }
    this.categoryToFunction[category].push(fun);
  }

  public getFunctionsForCategory(category: string): FunctionSpecSchema[] {
    if (!Object.keys(this.categoryToFunction).includes(category)) {
      printWarning(
        `No functions registered for category '${category}' - The default function handler will be used`
      );
      return [];
    }
    const functions = this.categoryToFunction[category];
    if (functions.length === 0) {
      printWarning(
        `No functions registered for category '${category}' - The default function handler will be used`
      );
      return [];
    }
    return functions;
  }

  public getHandler(functionName: string): IFunctionCallHandler {
    if (this.functionNameToHandler[functionName]) {
      return this.functionNameToHandler[functionName];
    }
    if (this.defaultHandler) {
      return this.defaultHandler;
    }
    throw new Error(
      `No function handler registered for function '${functionName}', and no default handler registered.`
    );
  }
}
