import * as tk from "terminal-kit";
import { Message } from "../gpt_maa_client/models/index.js";

const term = tk.default.terminal;

export const print = (...args: any[]): void => {
  term(...args, "\n");
};

export const printWarning = (...args: any[]): void => {
  term.yellow(...args, "\n");
};

export const printAssistant = (...args: any[]): void => {
  term.green("\n🤖 Assistant: ", args, "\n");
};

export const printUser = (...args: any[]): void => {
  term.magenta("\n😕 You: ", args, "\n");
};

export const printUserNoNewline = (...args: any[]): void => {
  term.magenta("\n😕 You: ", args);
};

export const printDetail = (...args: any[]): void => {
  term.grey("\n  ", ...args, "\n");
};

export const readInputFromUser = async (
  prompt: string
): Promise<string | null> => {
  printUserNoNewline(prompt);
  const userPrompt = await term.inputField().promise;
  return userPrompt ?? null;
};

export const dumpJson = (json: any) => {
  printDetail(JSON.stringify(json));
};

export const isQuit = (userInput: string | null): boolean => {
  if (!userInput) return true;

  return ["bye", "quit", "exit"].includes(userInput.trim().toLowerCase());
};

export const askUserIfOk = async (
  prompt: string,
  options: tk.Terminal.YesOrNoOptions
): Promise<{ yes: boolean; message: string | null }> => {
  while (true) {
    printAssistant(prompt);
    print("yes: ", options.yes);
    print("no: ", options.no);
    // term.yesOrNo freezes my git-bash terminal :(

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
