import yoctoSpinner, { Spinner } from "yocto-spinner";
import * as spinners from "cli-spinners";
import colors from "colors";
import * as inquirer from "@inquirer/prompts";
import { Message } from "../gpt_maa_client/models/index.js";

export const print = (...args: any[]): void => {
  console.log(...args, "\n");
};

const colorArgs = (cb: (s: string) => string, ...args: any[]): string[] => {
  return args.map((a) => cb(a));
};

export const printWarning = (...args: any[]): void => {
  console.log(colorArgs((a) => colors.yellow(a), args));
};

export const printAssistant = (...args: any[]): void => {
  console.log(
    colors.green("\n🤖 Assistant: "),
    ...args.map((a) => colors.green(a))
  );
};

export const printUser = (...args: any[]): void => {
  const cargs = colorArgs((a) => colors.magenta(a), args);
  console.log("\n😕 You: ", ...cargs, "\n");
};

export const printUserNoNewline = (...args: any[]): void => {
  const cargs = colorArgs((a) => colors.magenta(a), args);
  console.log("\n😕 You: ", ...cargs);
};

export const printDetail = (...args: any[]): void => {
  const cargs = colorArgs((a) => colors.gray(a), args);
  console.log("\n  ", ...cargs, "\n");
};

export const readInputFromUser = async (
  prompt: string
): Promise<string | null> => {
  const answer = await inquirer.input({ message: "\n😕 You: " + prompt });

  return answer.trim() ?? null;
};

export const dumpJson = (json: any) => {
  console.dir(json, { depth: null, colors: true });
};

export const isQuit = (userInput: string | null): boolean => {
  if (!userInput) return true;

  return ["quit", "bye", "exit", "stop"].includes(
    userInput.trim().toLowerCase()
  );
};

interface YesOrNoOptions {
  yes: string;
  no: string;
}

export const askUserIfOk = async (
  prompt: string,
  options: YesOrNoOptions
): Promise<{ yes: boolean; message: string | null }> => {
  while (true) {
    printAssistant(prompt);
    print("yes: ", options.yes);
    print("no: ", options.no);

    const userInput = await readInputFromUser("");
    if (!userInput) continue;

    if (isQuit(userInput))
      return {
        yes: false,
        message: userInput,
      };

    if (userInput.toLowerCase().startsWith("y"))
      return {
        yes: true,
        message: null,
      };

    return {
      yes: false,
      message: userInput,
    };
  }
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
    spinner: spinners.randomSpinner(),
  }).start();
};

export const stopSpinner = (spinner: Spinner): void => {
  if (spinner) spinner.success("[done]");
};
