
import { FunctionCallSchema } from "../gpt_maa_client/models/index.js";
import { IDictionary } from "./utils.js";

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
    protected registry: FunctionRegistry;
    protected functionCallNameToCallback: IDictionary<Callback> = {};

    constructor(registry: FunctionRegistry) {
        this.registry = registry;
    }

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

export const execute = (functionCalls: FunctionCallSchema[], registry: FunctionRegistry, onExecuteStart: () => void, onExecuteEnd: (errors: ExecutionError[]) => void): void => {
    onExecuteStart();

    const errors: ExecutionError[] = [];

    functionCalls.forEach(call => {
        try {
            if (!call.functionName) {
                errors.push({functionCallName: "<unknown>", error: "No function call name, so cannot identify a handler"})
                return;
            }

            const handler = registry.getHandler(call.functionName!);
            console.log(`Executing handler ${handler.name()} for function call ${call.functionName} from agent ${call.agentName}`)
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

    onExecuteEnd(errors);
};
