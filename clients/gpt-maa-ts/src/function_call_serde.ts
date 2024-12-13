import fs from "node:fs";
import path from "node:path";
import { FunctionCallBlackboardOutput } from "../gpt_maa_client/models/index.js";
import {
  FunctionCallBlackboardAccessor,
  TypeScriptBlackboardFormat,
} from "./function_call_blackboard_accessor.js";
import { getConfig } from "./util_config.js";
import { printDetail, printError, readInputFromUser } from "./utils_print.js";
import {
  findFilesByExtension,
  readJsonFromFile,
  writeJsonToFile,
} from "./util_file.js";
import { changeExtension } from "./util_file.js";

const SERIALIZED_BLACKBOARD_VERSION = "0.2";

interface SerializedBlackboard {
  blackboard: FunctionCallBlackboardOutput;
  file_schema_version: string;
}

export const load_blackboard_from_file = (
  filename: string
): FunctionCallBlackboardAccessor | null => {
  const filepath = path.join(getConfig().localBlackboardsDirPath, filename);

  if (!fs.existsSync(filepath)) {
    printError(
      "That file does not exist. Please use the list command to view the current files."
    );
    return null;
  }

  printDetail(`Loading blackboard from ${filepath}`);
  try {
    const json_data = readJsonFromFile(filepath) as SerializedBlackboard;

    return new FunctionCallBlackboardAccessor(json_data.blackboard);
  } catch (e: any) {
    console.error(e);
    printError(
      "Could not load that blackboard (the file could be old or a different format: FunctionCalling vs GraphQL)"
    );
    return null;
  }
};

export const save_blackboard_to_file = (
  blackboard: FunctionCallBlackboardAccessor,
  filename: string
): void => {
  filename = changeExtension(filename, `.${blackboard.format}.json`);
  const filepath = path.join(getConfig().localBlackboardsDirPath, filename);

  printDetail(`Saving blackboard to ${filepath}`);

  const serialized: SerializedBlackboard = {
    blackboard: blackboard,
    file_schema_version: SERIALIZED_BLACKBOARD_VERSION,
  };

  writeJsonToFile(filepath, serialized);
};

export const list_blackboard_files = (
  blackboard: FunctionCallBlackboardAccessor | null
): void => {
  const format = blackboard?.format ?? TypeScriptBlackboardFormat.function_call;

  const files = findFilesByExtension(
    getConfig().localBlackboardsDirPath,
    `${format}.json`
  );
  const filenames = files.map((f) => path.basename(f));
  printDetail(`Blackboard data files: ${filenames.join(", ")}`);
};
