import { FunctionCallSchema, FunctionSpecSchema } from "../gpt_maa_client/models/index.js";
import { FunctionRegistry, IFunctionCallHandler } from "./function_call_execution_registry.js";
import { IDictionary } from "./utils.js";

declare type Callback = (functionCall: FunctionCallSchema) => void;

/**
 * Base class for Function Handlers: each Handler can handle FunctionCalls for an 'area'.
 * - the Handler is used to actually execute the action specified by the REST API.
 */
export abstract class AreaHandlerBase implements IFunctionCallHandler
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
    protected registerFunctionHandler(fun: FunctionSpecSchema, category: string, functionHandler: Callback): void
    {
        if (!fun.functionName)
            throw new Error("The function must have a name")

        this.registry.registerHandler(fun, category, this);
        this.functionCallNameToCallback[fun.functionName] = functionHandler;
    }

    HandleFunctionCall(functionCall: FunctionCallSchema): void {
        this.functionCallNameToCallback[functionCall.functionName!](functionCall);
    }

    name(): string {
        return this.nameImplementation();
    }

    protected abstract nameImplementation(): string;
}

/**
 * A Default 'catch other functions' Area Handler which can call one registered callback.
 * - the intention is to allow development without having to implement individual handlers for every function.
 */
export class DefaultAreaHandler extends AreaHandlerBase
{
    private defaultFunctionHandler: Callback;

    constructor(registry: FunctionRegistry, action: Callback)
    {
        super(registry);
        this.defaultFunctionHandler = action;
        registry.registerDefaultHandler(this);
    }

    HandleFunctionCall(functionCall: FunctionCallSchema): void {
        this.defaultFunctionHandler(functionCall);
    }

    protected nameImplementation(): string
    {
        return "[default handler]";
    }
}
