import path from "node:path";
import { readJsonFromFile } from "./util_file.js";

export interface Config
{
    baseurl: string;
    isDebug: boolean;
    localAgentsDirPath: string;
    localBlackboardsDirPath: string;
}

export const getConfig = (): Config =>
{
    const filename = "config.json";
    const filepath = path.join(process.cwd(), filename)
    return readJsonFromFile(filepath) as Config
}
