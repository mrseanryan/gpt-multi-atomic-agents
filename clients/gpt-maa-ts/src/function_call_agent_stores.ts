import {
  IAgentStore,
  instanceOfSerializableAgentWithCategories,
  SerializableAgentWithCategories,
} from "./serializable_agent.js";
import { getConfig } from "./util_config.js";
import { findFilesByExtension, readJsonFromFile } from "./util_file.js";
import { printWarning } from "./utils_print.js";

class LocalFunctionCallAgentStore implements IAgentStore {
  loadAgents(): SerializableAgentWithCategories[] {
    const files = findFilesByExtension(
      getConfig().localAgentsDirPath,
      ".agent.json"
    );

    const agents: SerializableAgentWithCategories[] = [];
    files.forEach((file) => {
      const doc = readJsonFromFile(file);

      if (instanceOfSerializableAgentWithCategories(doc)) {
        agents.push(doc);
      } else {
        printWarning(
          `Could not load agent file ${file} - it does not match the expected structure SerializableAgentWithCategories`
        );
      }
    });

    return agents;
  }
}

export const getAgentStores = (): IAgentStore[] => [
  new LocalFunctionCallAgentStore(),
];

export const loadCustomAgents = (): SerializableAgentWithCategories[] =>
  getAgentStores()
    .map((a) => a.loadAgents())
    .flat();
