import yoctoSpinner, { Spinner } from "yocto-spinner";
import * as spinners from "cli-spinners";
import colors from "colors";
import { Message } from "../gpt_maa_client/models/index.js";
import { isDebugActive } from "./util_config.js";

export const print = (...args: any[]): void => {
  console.log(...args);
};

const colorArgs = (cb: (s: string) => string, ...args: any[]): string[] => {
  return args.map((a) => cb(a));
};

export const printWarning = (...args: any[]): void => {
  console.log(...colorArgs((a) => colors.yellow(a), args));
};

export const printError = (...args: any[]): void => {
  console.log(...colorArgs((a) => colors.red(a), args));
};

const EMOJI_ASSISTANT = "🤖";
export const EMOJI_USER = "😕";

export const printAssistant = (...args: any[]): void => {
  console.log(
    colors.green(`${EMOJI_ASSISTANT} Assistant: `),
    ...args.map((a) => colors.green(a))
  );
};

export const printUser = (...args: any[]): void => {
  const cargs = colorArgs((a) => colors.magenta(a), args);
  console.log(`${EMOJI_USER} You: `, ...cargs);
};

export const printUserNoNewline = (...args: any[]): void => {
  const cargs = colorArgs((a) => colors.magenta(a), args);
  console.log(`${EMOJI_USER} You: `, ...cargs);
};

export const printDetail = (...args: any[]): void => {
  const cargs = colorArgs((a) => colors.gray(a), args);
  console.log("  ", ...cargs);
};

export const dumpJson = (json: any) => {
  if (isDebugActive()) {
    dumpJsonAlways(json);
  }
};

export const dumpJsonAlways = (json: any) => {
  console.dir(json, { depth: null, colors: true });
};

export const printMessages = (messages: Message[]): void => {
  messages.forEach((message) => {
    if (message.role == "user") printUser(message.message);
    else printAssistant(message.message);
  });
};

export const startTimer = (name: string): string => {
  console.time(name);
  return name;
};

export const printTimeTaken = (name: string): void => {
  console.timeEnd(name);
};

export const showSpinner = (): Spinner => {
  return yoctoSpinner({
    text: "Processing…",
    spinner: spinners.default.sand, // spinners.randomSpinner(), - ref: https://jsfiddle.net/sindresorhus/2eLtsbey/embedded/result/
  }).start();
};

export const stopSpinner = (spinner: Spinner): void => {
  if (spinner) spinner.success("[done]");
};
