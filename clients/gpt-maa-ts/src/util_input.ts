import * as inquirer from "@inquirer/prompts";

import { EMOJI_USER, print, printAssistant } from "./utils_print.js";

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

const isQuit = (userInput: string | null): boolean => {
  if (!userInput) return true;

  return ["quit", "bye", "exit", "stop"].includes(
    userInput.trim().toLowerCase()
  );
};

interface AskUserOption {
  name: string;
  description: string;
  needsUserInput: boolean;
}

interface AskUserOptions {
  prompt: string;
  options: AskUserOption[];
}

interface AskUserChosen {
  chosen: AskUserOption;
  userInput: string | null;
}

export const askUserWithOptions = async (
  options: AskUserOptions
): Promise<AskUserChosen> => {
  const answer = await inquirer.select({
    message: options.prompt,
    choices: options.options.map((o) => {
      return {
        name: o.name,
        value: o.name,
        description: o.description,
      };
    }),
  });

  const selected = options.options.filter((o) => o.name == answer);
  switch (selected.length) {
    case 0:
      throw new Error("No options were selected");
    case 1:
      const selectedOne = selected[0];
      if (selectedOne.needsUserInput) {
        const userInput = await readInputFromUser(
          "Please provide more details."
        );
        return {
          chosen: selectedOne,
          userInput: userInput,
        };
      }
      return {
        chosen: selectedOne,
        userInput: null,
      };
    default:
      throw new Error("Multiple options were selected");
  }
};

export const readInputFromUser = async (
  prompt: string
): Promise<string | null> => {
  printAssistant(prompt);
  const answer = await inquirer.input({
    message: `${EMOJI_USER} You: `,
  });

  return answer.trim() ?? null;
};
