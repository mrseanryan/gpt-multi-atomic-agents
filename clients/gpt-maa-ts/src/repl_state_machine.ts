// State Machine to manage the state of the REPL command loop.
// - helps with handling user's approval of whether to continue
// - also helps allow for running debug commands, without resetting the state

import { dumpJson, printAssistant, printDetail } from "./utils_print.js";
import { FunctionRegistry } from "./function_call_execution_registry.js";
import {
  AgentExecutionPlanSchema,
  FunctionAgentDefinitionMinimal,
} from "../gpt_maa_client/models/index.js";
import {
  convertSerializableAgentToContractAgent,
  SerializableAgentWithCategories,
} from "./serializable_agent.js";
import { FunctionCallBlackboardAccessor } from "./function_call_blackboard_accessor.js";
import { generate_plan } from "./function_call_planner.js";
import { generate_mutations } from "./function_call_generator.js";
import { PostsClient } from "../gpt_maa_client/postsClient.js";
import {
  execute,
  ExecuteStartResult,
  ExecutionError,
} from "./function_call_executor.js";
import { IReplCommandContext } from "./repl_commands.js";

/**
 * Allow States to manipulate the Context, but NOT to change state.
 */
interface IReplStateContext {
  getClient(): PostsClient;
  getUserPrompt(): string;
  getChatAgentDescription(): string;
  executionPlan: AgentExecutionPlanSchema | undefined;
  getPreviousPrompt(): string | null;
  blackboardAccessor: FunctionCallBlackboardAccessor | null;
  getCombinedAgents(): FunctionAgentDefinitionMinimal[];
}

export abstract class ReplState {
  public abstract getName(): string;
  public abstract handleRequest(context: IReplStateContext): Promise<void>;
}

export class PlanReplState extends ReplState {
  public getName = (): string => "Plan";

  public async handleRequest(context: IReplStateContext): Promise<void> {
    context.executionPlan = await generate_plan(
      context.getClient(),
      context.getUserPrompt(),
      context.getCombinedAgents(),
      context.getChatAgentDescription(),
      context.executionPlan,
      context.blackboardAccessor?.get_previous_messages() ?? null
    );
  }
}

export class GenerateReplState extends ReplState {
  public getName = (): string => "Generate";

  public async handleRequest(context: IReplStateContext): Promise<void> {
    context.blackboardAccessor = await generate_mutations(
      context.getClient(),
      context.getUserPrompt(),
      context.getCombinedAgents(),
      context.getChatAgentDescription(),
      context.executionPlan,
      context.blackboardAccessor
    );
    if (!context.blackboardAccessor) {
      throw new Error("No blackboard accessor was returned!");
    }
  }
}

export class ExecuteReplState extends ReplState {
  private functionRegistry: FunctionRegistry;
  private onExecuteStart: () => Promise<ExecuteStartResult>;
  private onExecuteEnd: (
    errors: ExecutionError[],
    blackboardAccessor: FunctionCallBlackboardAccessor
  ) => Promise<void>;

  constructor(
    functionRegistry: FunctionRegistry,
    onExecuteStart: () => Promise<ExecuteStartResult>,
    onExecuteEnd: (
      errors: ExecutionError[],
      blackboardAccessor: FunctionCallBlackboardAccessor
    ) => Promise<void>
  ) {
    super();
    this.functionRegistry = functionRegistry;
    this.onExecuteStart = onExecuteStart;
    this.onExecuteEnd = onExecuteEnd;
  }

  public getName = (): string => "Execute";

  public async handleRequest(context: IReplStateContext): Promise<void> {
    // Execute the Function Calls using our Handlers
    if (!context.blackboardAccessor) {
      throw new Error("Blackboard not set, even after generate");
    }

    printAssistant("Performing your requested tasks now...");
    await execute(
      this.functionRegistry,
      context.blackboardAccessor,
      this.onExecuteStart,
      this.onExecuteEnd
    );
  }
}

const getCombinedAgentDefinitions = (
  agentDefinitions: FunctionAgentDefinitionMinimal[],
  customAgents: SerializableAgentWithCategories[],
  functionRegistry: FunctionRegistry
): FunctionAgentDefinitionMinimal[] => {
  return agentDefinitions.concat(
    customAgents.map((a) =>
      convertSerializableAgentToContractAgent(a, functionRegistry)
    )
  );
};

export class ReplContext implements IReplStateContext, IReplCommandContext {
  private state: ReplState | null = null;
  private readonly client: PostsClient;
  private readonly chatAgentDescription: string;

  userPrompt: string | null = null;

  executionPlan: AgentExecutionPlanSchema | undefined = undefined;
  previousPrompt: string | null = null;
  blackboardAccessor: FunctionCallBlackboardAccessor | null = null;

  functionRegistry: FunctionRegistry;
  agentDefinitions: FunctionAgentDefinitionMinimal[];
  customAgents: SerializableAgentWithCategories[];

  generateNeedsApproval: boolean = false;

  constructor(
    client: PostsClient,
    chatAgentDescription: string,
    functionRegistry: FunctionRegistry,
    agentDefinitions: FunctionAgentDefinitionMinimal[],
    customAgents: SerializableAgentWithCategories[]
  ) {
    this.client = client;
    this.chatAgentDescription = chatAgentDescription;
    this.functionRegistry = functionRegistry;
    this.agentDefinitions = agentDefinitions;
    this.customAgents = customAgents;
  }

  getClient = (): PostsClient => this.client;
  getChatAgentDescription = (): string => this.chatAgentDescription;
  getPreviousPrompt = (): string | null => this.previousPrompt;

  public getCombinedAgents = () =>
    getCombinedAgentDefinitions(
      this.agentDefinitions,
      this.customAgents,
      this.functionRegistry
    );

  getState = (): ReplState | null => this.state;
  getUserPrompt(): string {
    if (!this.userPrompt) throw new Error("User prompt not set");
    return this.userPrompt;
  }

  public setState(state: ReplState): void {
    this.state = state;
    printDetail(`(State changed to ${this.state.getName()})`);
  }

  public async request(): Promise<void> {
    if (!this.state) throw Error("State is not set!");
    await this.state.handleRequest(this);
  }
}
