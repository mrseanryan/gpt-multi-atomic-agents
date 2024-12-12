import * as tk from "terminal-kit";
import { Message } from "../gpt_maa_client/models/index.js";

const term = tk.default.terminal

export const print = (...args: any[]): void => {
    term(...args, "\n");
} 

export const printWarning = (...args: any[]): void  => {
    term.yellow(...args, "\n");
}

export const printAssistant = (...args: any[]): void => {
    term.green("\n🤖 Assistant: ", args, "\n")
}

export const printUser = (...args: any[]): void => {
    term.magenta("\n😕 You: ", args, "\n")
}

export const printUserNoNewline = (...args: any[]): void => {
    term.magenta("\n😕 You: ", args)
}

export const printDetail = (...args: any[]): void => {
    term.grey("\n  ", ...args, "\n")
}

export const readInputFromUser = async (prompt: string): Promise<string|null> => {
    printUserNoNewline(prompt)
    const userPrompt = await term.inputField().promise
    return userPrompt ?? null;
}

export const dumpJson = (json: any) => {
    printDetail(JSON.stringify(json))
}

export const askUserIfOk = async (prompt: string, options: tk.Terminal.YesOrNoOptions): Promise<boolean> => {
    while(true) {
        printAssistant(prompt)
        print("yes: ", options.yes)
        print("no: ", options.no)
        // term.yesOrNo freezes my git-bash terminal :(

        const user = await readInputFromUser("")
        if (!user)
            continue

        if (user.toLowerCase().startsWith('y'))
            return true

        if (user.toLowerCase().startsWith('n'))
            return false

        printAssistant("I'm sorry, I do not understand. Please type y<enter> or n<enter>")
    }
}

export const printMessages = (messages: Message[]) : void => {
    messages.forEach(message => {
        if (message.role == "user")
            printUser(message.message)
        else printAssistant(message.message)
    })
}