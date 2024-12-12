import { AgentExecutionPlanSchema, FunctionAgentDefinitionMinimal } from "../gpt_maa_client/models/index.js"
import { FunctionCallBlackboardAccessor } from "./function_call_blackboard_accessor.js"
import { execute } from "./function_call_executor.js"
import { createClient, generate_mutations, generate_plan } from "./index.js"
import { functionRegistry } from "./resources_test_domain.js"
import { askUserIfOk, dumpJson, isQuit, printAssistant, printDetail, printMessages, readInputFromUser } from "./utils_print.js";
import { PostsClient } from "../gpt_maa_client/postsClient.js";

export const chatWithAgentsRepl = async (agentDefinitions: FunctionAgentDefinitionMinimal[], chatAgentDescription: string, baseurl: string): Promise<FunctionCallBlackboardAccessor|null> => {
    printAssistant("Hello, can may I help you?")
    const client: PostsClient = createClient(baseurl)

    let executionPlan: AgentExecutionPlanSchema|undefined = undefined

    let previousPrompt: string|null = null

    while(true) {
        const userPrompt = previousPrompt ?? await readInputFromUser("");
        // TODO: check for other commands, not just quitting
        if (!userPrompt || isQuit(userPrompt)) {
            printAssistant("Goodbye!\n")
            return null;
        }
        previousPrompt = null

        executionPlan = await generate_plan(client, userPrompt, agentDefinitions, chatAgentDescription, executionPlan)
    
        printAssistant(executionPlan?.chatMessage)
        
        if (isOnlyChat(executionPlan?.recommendedAgents))
            continue

        const doContinue = await askUserIfOk("Would you like to go ahead with that plan?", {
            yes: "Go ahead",
            no: "I'd like to change something"
        })
        if (!doContinue.yes) {
            previousPrompt = doContinue.message
            continue
        }

        const blackboardAccessor = await generate_mutations(client, userPrompt, agentDefinitions, chatAgentDescription, executionPlan)
        if (!blackboardAccessor) {
            throw new Error("No blackboard accessor was returned!")
        }
        
        // =================================================
        // Display the messages from the Agents
        const messages = blackboardAccessor.get_new_messages();
        printMessages(messages);

        const doCreateApp = await askUserIfOk("Would you like to apply those changes now?", {
            yes: "Go ahead",
            no: "I'd like to change something"
        })
        if (!doCreateApp.yes) {
            previousPrompt = doContinue.message
            continue
        }

        // =================================================
        // Execute the Function Calls using our Handlers
        printAssistant("Performing your requested tasks now...")
        dumpJson(blackboardAccessor.get_new_functions())
        const onExecuteStart = async () => {
            console.log("(execution started)")
        }
        const onExecuteEnd = async () => {
            console.log("(execution ended)")
        }
        await execute(blackboardAccessor.get_new_functions(), functionRegistry, onExecuteStart, onExecuteEnd);

        printAssistant("Is there anything else I can help with?")
    }
}

function isOnlyChat(recommendedAgents: import("./index.js").RecommendedAgent[] | null | undefined) {
    if (!recommendedAgents) {
        return true
    }

    return (recommendedAgents.length === 1 && recommendedAgents[0].agentName == "chat")
}