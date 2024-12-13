
import { FunctionCallSchema } from "../gpt_maa_client/models/index.js";
import { IDictionary } from "./utils.js";
import { print, printTimeTaken, showSpinner, startTimer, stopSpinner } from "./utils_print.js";

export interface IFunctionCallHandler
{
    name(): string;
    Handle(functionCall: FunctionCallSchema): void;
}

export class FunctionRegistry
{
    private defaultHandler: IFunctionCallHandler|null = null;
    private functionNameToHandler: IDictionary<IFunctionCallHandler> = {};

    public registerDefaultHandler(handler: IFunctionCallHandler): void {
        if (this.defaultHandler) {
            throw new Error("A default handler is already registered");
        }

        this.defaultHandler = handler;
    }

    public registerHandler(functionName: string, handler: IFunctionCallHandler): void {
        if (this.functionNameToHandler[functionName])
            throw new Error(`A handler is already registered for function ${functionName}`);

        this.functionNameToHandler[functionName] = handler;
    }

    public getHandler(functionName: string): IFunctionCallHandler {
        if (this.functionNameToHandler[functionName]) {
            return this.functionNameToHandler[functionName];
        }
        if (this.defaultHandler) {
            return this.defaultHandler;
        }
        throw new Error(`No function handler registered for function '${functionName}', and no default handler registered.`);
    }
}


declare type Callback = (functionCall: FunctionCallSchema) => void;

export abstract class HandlerBase implements IFunctionCallHandler
{
    protected readonly registry: FunctionRegistry;
    protected readonly functionCallNameToCallback: IDictionary<Callback> = {};

    protected constructor(registry: FunctionRegistry)
    {
        this.registry = registry;
    }

    /**
     * Register a handler to handler the given Function Call.
     *
     * warning: do NOT use 'this' in your function (consider 'self').
     */
    protected registerFunction(functionName: string, handler: Callback): void
    {
        this.registry.registerHandler(functionName, this);
        this.functionCallNameToCallback[functionName] = handler;
    }

    Handle(functionCall: FunctionCallSchema): void {
        this.functionCallNameToCallback[functionCall.functionName!](functionCall);
    }

    name(): string {
        return this.nameImplementation();
    }

    protected abstract nameImplementation(): string;
}

export class DefaultHandler extends HandlerBase
{
    private defaultAction: Callback;

    constructor(registry: FunctionRegistry, action: Callback)
    {
        super(registry);
        this.defaultAction = action;
        registry.registerDefaultHandler(this);
    }

    Handle(functionCall: FunctionCallSchema): void {
        this.defaultAction(functionCall);
    }

    protected nameImplementation(): string
    {
        return "[default handler]";
    }
}

export interface ExecutionError
{
    functionCallName: string;
    error: string;
}

export const execute = async (functionCalls: FunctionCallSchema[], registry: FunctionRegistry, onExecuteStart: () => Promise<void>, onExecuteEnd: (errors: ExecutionError[]) => Promise<void>): Promise<void> => {
    const timer = startTimer("execute")

    let spinner = showSpinner()
    await onExecuteStart();
    stopSpinner(spinner)

    const errors: ExecutionError[] = [];

    functionCalls.forEach(call => {
        try {
            if (!call.functionName) {
                errors.push({functionCallName: "<unknown>", error: "No function call name, so cannot identify a handler"})
                return;
            }

            const handler = registry.getHandler(call.functionName!);
            print(`Executing handler ${handler.name()} for function call ${call.functionName} from agent ${call.agentName}`)

            handler.Handle(call);
        }
        catch(e: any) {
            if (e instanceof(Error)) {
                errors.push({ functionCallName: call.functionName!, error: e.message});
            } else {
                errors.push({ functionCallName: call.functionName!, error: e });
            }
        }
    });

    spinner = showSpinner()
    await onExecuteEnd(errors);
    stopSpinner(spinner)
    printTimeTaken(timer)
};
