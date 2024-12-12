import { FunctionCallBlackboardOutput, FunctionCallSchema, Message } from "../gpt_maa_client/models/index.js";

export class FunctionCallBlackboardAccessor
{
    private blackboard: FunctionCallBlackboardOutput; // The inner blackboard - should only be used to send to REST API, not used directly by the client

    constructor(blackboard: FunctionCallBlackboardOutput)
    {
        this.blackboard = blackboard;
    }

    public get_new_functions(): FunctionCallSchema[]
    {
        // Get the new function calls which the client needs to execute. After executing, the client should call set_user_data() to pass in the updated and/or missing data.
        if (!this.blackboard.internalNewlyGeneratedFunctions)
            return [];
        return this.blackboard.internalNewlyGeneratedFunctions;
    }

    public get_new_messages(): Message[]
    {
        // Gets newly created messages that should be displayed to the user.
        if (!this.blackboard.internalNewlyGeneratedMessages)
            return [];
        return this.blackboard.internalNewlyGeneratedMessages;
    }

    private _reset() {
        // Resets newly created functions, to prepare for next generation
        this.blackboard.internalNewlyGeneratedFunctions = [];
        this.blackboard.internalNewlyGeneratedMessages = [];
    }

    public set_user_data(user_data: FunctionCallSchema[])
    {
        // Receives the new version of user data, by setting the function-calls list, so is ready for next generation.
        this._reset()
        this.blackboard.internalPreviouslyGeneratedFunctions = user_data;
    }

    public get_internal_blackboard(): FunctionCallBlackboardOutput
    {
        return this.blackboard;
    }
}
