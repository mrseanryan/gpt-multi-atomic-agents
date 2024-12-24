// TS e2e example, consuming the TS framework and using 3 'Sim Life' Agents to generate Function Calls. A basic Handler is used during Execution, to output a DOT file.

import {
  ExecuteStartResult,
  ExecutionError,
  FunctionAgentDefinitionMinimal,
  FunctionCallBlackboardAccessor,
  FunctionCallSchema,
  FunctionSpecSchema,
  handleUserPrompt,
  ParameterSpec,
  printError,
} from "gpt-maa-ts";
import {
  DefaultAreaHandler,
  execute,
  FunctionRegistry,
  AreaHandlerBase,
} from "gpt-maa-ts";

// =================================================
// Define the Functions
const areaParameter: ParameterSpec = {
  name: "area",
  type: "string",
  allowedValues: ["front", "back"],
};

const mowLawnFunction: FunctionSpecSchema = {
  functionName: "MowLawn",
  description: "Mow the lawn and tidy it up",
  parameters: [areaParameter],
};
const produceCutGrassFunction: FunctionSpecSchema = {
  functionName: "ProduceCutGrass",
  description: "Produce cut grass waster",
  parameters: [areaParameter],
};

const mowerOutputFunctions: FunctionSpecSchema[] = [
  mowLawnFunction,
  produceCutGrassFunction,
];

const furnitureMoverOutputFunctions: FunctionSpecSchema[] = [
  {
    functionName: "MoveFurniture",
    description:
      "Move furniture so it is not in the way, and move back again when appropriate.",
    parameters: [areaParameter],
  },
];

const wasteDisposerOutputFunctions: FunctionSpecSchema[] = [
  {
    functionName: "CollectWaste",
    description: "Collect waste from an area",
    parameters: [areaParameter],
  },
  {
    functionName: "TakeWasteToCollectionSite",
    description:
      "Take previously collected waste from an area, to a collection site",
    parameters: [
      areaParameter,
      {
        name: "site_name",
        type: "string",
      },
    ],
  },
];

// =================================================
// Define our Handlers so we can execute any generated Function Calls

const functionRegistry = new FunctionRegistry();

const handleMowLawn = (functionCall: FunctionCallSchema): void => {
  console.log("<mowing the lawn>");
  console.log(`  params:`, functionCall.parameters);
};

const handleProduceCutGrass = (functionCall: FunctionCallSchema): void => {
  console.log("<producing cut grass>");
  console.log(`  params:`, functionCall.parameters);
};

class LawnHandler extends AreaHandlerBase {
  constructor(registry: FunctionRegistry) {
    super(registry);
    this.registerFunctionHandler(mowLawnFunction, "lawn", (fc) =>
      handleMowLawn(fc)
    );
    this.registerFunctionHandler(produceCutGrassFunction, "lawn", (fc) =>
      handleProduceCutGrass(fc)
    );
  }

  protected nameImplementation(): string {
    return "Lawn Handler";
  }
}

// Create the handlers (they register themselves)
new DefaultAreaHandler(functionRegistry, (functionCall: FunctionCallSchema) => {
  console.log(
    `[default handler] for function call: ${functionCall.functionName}`,
    functionCall.parameters
  );
});
new LawnHandler(functionRegistry);

// TODO add WasteHandler, FurnitureHandler

// =================================================
// Declare the Agents in terms of the shared Functions
const lawnMowerAgent: FunctionAgentDefinitionMinimal = {
  agentName: "Lawn Mower",
  description: "Knows how to mow lawns",
  acceptedFunctions: mowerOutputFunctions,
  functionsAllowedToGenerate: mowerOutputFunctions,
  topics: ["garden", "lawn", "grass"],
  agentParameters: {
    additionalData: {
      "lawn-condition": [],
    },
  },
};

const furnitureMoverAgent: FunctionAgentDefinitionMinimal = {
  agentName: "Furniture Mover",
  description:
    "Knows how to move furniture to different parts of garden, and move in or out of garden",
  acceptedFunctions: [...furnitureMoverOutputFunctions, mowLawnFunction], // The furniture mover can observe when the lawn-mower needs to access that area
  functionsAllowedToGenerate: furnitureMoverOutputFunctions,
  topics: ["furniture"],
  agentParameters: {
    additionalData: {
      "furniture-kind": [],
    },
  },
};

const wasteDisposerAgent: FunctionAgentDefinitionMinimal = {
  agentName: "Waste Disposer",
  description: "Knows how to collect and dispose of waste",
  acceptedFunctions: [...wasteDisposerOutputFunctions, produceCutGrassFunction], // The waste disposer can observe when the lawn-mower has generated waste
  functionsAllowedToGenerate: wasteDisposerOutputFunctions,
  topics: ["waste", "dispose"],
};

const agentDefinitions: FunctionAgentDefinitionMinimal[] = [
  lawnMowerAgent,
  furnitureMoverAgent,
  wasteDisposerAgent,
];

// =================================================
// Chat with the Agents
const chatAgentDescription =
  "Handles questions about household chores such as garden, garden furniture and waste maintenance.";

await handleUserPrompt(
  "What can you do?",
  agentDefinitions,
  chatAgentDescription
);
const blackboardAccessor = await handleUserPrompt(
  "Mow the dirty lawn, dealing with any old lawn furniture and waste. After mowing make sure waste is disposed of.",
  agentDefinitions,
  chatAgentDescription
);

if (!blackboardAccessor) {
  throw new Error("No blackboard accessor was returned!");
}

// =================================================
// Display the messages from the Agents
const messages = blackboardAccessor.get_new_messages();
console.log(messages);

// =================================================
// Execute the Function Calls using our Handlers
blackboardAccessor.get_new_functions();
const onExecuteStart = async (): Promise<ExecuteStartResult> => {
  console.log("(execution started)");
  return {
    isOkToContinue: true,
    alsoExecutePreviousFunctions: false
  }
};
const onExecuteEnd = async (
  errors: ExecutionError[],
  blackboardAccessor: FunctionCallBlackboardAccessor
): Promise<void> => {
  console.log("(execution ended)");
  if (errors.length) {
    printError(errors);
  }
    // Assuming that client has applied all functions, and wants to continue from that state:
    const new_user_data = blackboardAccessor.get_new_functions();
    blackboardAccessor.set_user_data(new_user_data);
};
await execute(
  functionRegistry,
  blackboardAccessor,
  onExecuteStart,
  onExecuteEnd
);
