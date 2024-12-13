import { FunctionAgentDefinitionMinimal, FunctionAgentDefinitionMinimal_agent_parameters, FunctionSpecSchema } from "../gpt_maa_client/models/index.js";
import { FunctionRegistry } from "./function_call_execution_registry.js";
import { IDictionary } from "./utils.js";

/**
 * Client-side definition of an Agent, which is serializable and specifies its Inputs and Outputs in terms of Categories.
 * - this is to allow for 'dynamic' or Custom agents, which are not hard-coded but are read from some 'Agent Store', and could even be editted or created at run-time.
 * 
 * - categories are used rather than function names, to have a looser coupling with which functions are actually available on the client.
 *   - this makes it easier to share agents between clients (for example via an Agent Store).
 */
export interface SerializableAgentWithCategories
{
    agentName: string,
    description: string,
    // TODO: For more advanced prompting, add `steps: string[]` (also need to add to the REST API and server side framework)
    acceptedFunctionCategories: string[],
    functionCategoriesAllowedToGenerate: string[],
    topics: string[]
    agentParameters: string[];
}

/**
 * Interfaces do not exist at runtime (JavaScript is duck-typed)
 */
export function instanceOfSerializableAgentWithCategories(object: any): object is SerializableAgentWithCategories
{
    return 'agentName' in object && 'description' in object && 'acceptedFunctionCategories' in object && 'functionCategoriesAllowedToGenerate' in object && 'topics' in object && 'agentParameters' in object;
}

/**
 * Takes a Serializable Agent (that was read from some Agent Store) and converts to to a 'contract' Agent, suitable for use with the REST API.
 * - the Serializable Agent is very loosely coupled to Functions, by means of categories.
 * - when converting, we use the FunctionRegistry to resolve the Category to relevant function(s).
 */
export const convertSerializableAgentToContractAgent = (serializableAgent: SerializableAgentWithCategories, functionRegistry: FunctionRegistry): FunctionAgentDefinitionMinimal => {
    const agentParameters: FunctionAgentDefinitionMinimal_agent_parameters = {}
    const agentParametersDict = (agentParameters as IDictionary<string[]>)
    serializableAgent.agentParameters.forEach(param => agentParametersDict[param] = [])

    // Resolve the input and output functions, by category
    let acceptedFunctions: FunctionSpecSchema[] = []
    let functionsAllowedToGenerate: FunctionSpecSchema[] = []

    serializableAgent.acceptedFunctionCategories.forEach(category => {
        acceptedFunctions = acceptedFunctions.concat(functionRegistry.getFunctionsForCategory(category))
    })
    serializableAgent.functionCategoriesAllowedToGenerate.forEach(category => {
        functionsAllowedToGenerate = functionsAllowedToGenerate.concat(functionRegistry.getFunctionsForCategory(category))
    })

    return {
        agentName: serializableAgent.agentName,
        description: serializableAgent.description,
        acceptedFunctions: acceptedFunctions,
        functionsAllowedToGenerate: functionsAllowedToGenerate,
        agentParameters: agentParameters,
        topics: serializableAgent.topics
    }
}

export interface IAgentStore
{
    loadAgents(): SerializableAgentWithCategories[]
}
