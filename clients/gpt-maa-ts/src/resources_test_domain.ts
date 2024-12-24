// Resource: an example of a 'household chores bots' domain.
import {
  FunctionAgentDefinitionMinimal,
  FunctionCallSchema,
  FunctionCallSchema_parameters,
  FunctionSpecSchema,
  ParameterSpec,
} from "../gpt_maa_client/models/index.js";
import {
  DefaultAreaHandler,
  AreaHandlerBase,
} from "./function_call_execution_handlers.js";
import { FunctionRegistry } from "./function_call_execution_registry.js";
import { dumpJsonAlways, print, printDetail } from "./utils_print.js";

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
  description: "Produce cut grass as waste",
  parameters: [areaParameter],
};

const textOutputFunction: FunctionSpecSchema = {
  functionName: "AddText",
  description: "Generate text",
  parameters: [
    {
      name: "text",
      type: "string",
    },
  ],
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

export const functionRegistry = new FunctionRegistry();

const printParameters = (
  parameters: FunctionCallSchema_parameters | null | undefined
) => {
  printDetail(`  parameters:`);
  dumpJsonAlways(parameters);
};

class LawnHandler extends AreaHandlerBase {
  constructor(registry: FunctionRegistry) {
    super(registry);

    const self = this;
    this.registerFunctionHandler(mowLawnFunction, "lawn", (fc) =>
      self.handleMowLawn(fc)
    );
    this.registerFunctionHandler(produceCutGrassFunction, "lawn-waste", (fc) =>
      self.handleProduceCutGrass(fc)
    );
  }
  private handleMowLawn(fc: FunctionCallSchema): void {
    print("<mowing the lawn>");
    printParameters(fc.parameters);
  }
  private handleProduceCutGrass(fc: FunctionCallSchema): void {
    print("<producing cut grass>");
    printParameters(fc.parameters);
  }

  protected nameImplementation(): string {
    return "Lawn Handler";
  }
}

class WasteDisposalHandler extends AreaHandlerBase {
  constructor(registry: FunctionRegistry) {
    super(registry);

    const category = "waste";

    const self = this;
    wasteDisposerOutputFunctions.forEach((wd) =>
      self.registerFunctionHandler(wd, category, (fc) => self.handleWaste(fc))
    );
  }

  private handleWaste(fc: FunctionCallSchema): void {
    print(`<handling waste from ${fc.functionName}>`);
    printDetail;
  }

  protected nameImplementation(): string {
    return "Waste Handler";
  }
}

// Create the handlers (they register themselves)
const defaultHandler = new DefaultAreaHandler(
  functionRegistry,
  (functionCall: FunctionCallSchema) => {
    printDetail(
      `[default handler] for function call: ${functionCall.functionName}`,
      functionCall.parameters
    );
  }
);
new LawnHandler(functionRegistry);
new WasteDisposalHandler(functionRegistry);

// Register other functions that are not used by the hard-coded agents:
functionRegistry.registerHandler(textOutputFunction, "text", defaultHandler);

// TODO add FurnitureHandler

// =================================================
// Declare the Agents in terms of the shared Functions
const lawnMowerAgent: FunctionAgentDefinitionMinimal = {
  agentName: "Lawn Mower",
  description: "Knows how to mow lawns",
  acceptedFunctions: mowerOutputFunctions,
  functionsAllowedToGenerate: mowerOutputFunctions,
  topics: ["garden", "lawn", "grass"],
};

const furnitureMoverAgent: FunctionAgentDefinitionMinimal = {
  agentName: "Furniture Mover",
  description:
    "Knows how to move furniture to different parts of garden, and move in or out of garden",
  acceptedFunctions: [...furnitureMoverOutputFunctions, mowLawnFunction], // The furniture mover can observe when the lawn-mower needs to access that area
  functionsAllowedToGenerate: furnitureMoverOutputFunctions,
  topics: ["furniture"],
};

// note: The WasteDisposer Agent is a 'custom' agent defined in a JSON file ('waste-diposer.agent.json').
// - this is an example of reading 'custom' agents from an Agent Store.

export const agentDefinitions: FunctionAgentDefinitionMinimal[] = [
  lawnMowerAgent,
  furnitureMoverAgent,
];

export const chatAgentDescription =
  "Handles questions about household chores such as garden, garden furniture and waste maintenance.";
