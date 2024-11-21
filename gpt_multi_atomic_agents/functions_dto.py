from enum import StrEnum
from atomic_agents.agents.base_agent import (
    BaseIOSchema,
)
from pydantic import Field


class ParameterType(StrEnum):
    """Defines the type of a parameter."""
    int = "int"
    float = "float"
    string = "string"
    date = "datetime"
    # TODO: add more parameter types

class ParameterSpec(BaseIOSchema):
    """Defines one parameter of a function, including its name, type and allowed values. If allowed values are empty, then values must match the 'type'."""
    name: str
    type: ParameterType
    allowed_values: list[str] = Field(default_factory=lambda: [])

class FunctionSpecSchema(BaseIOSchema):
    """This schema represents the definition of a function call that can be generated."""
    agent_name: str = Field(description="The name of the agent that generated the function calls")  # TODO review, this makes the f/w less flexible
    description: str = Field(description="Describes what the function does")
    function_name: str = Field(description="The name of the function")
    parameters: list[ParameterSpec] = Field(description="Named parameters of the function")

class FunctionCallSchema(BaseIOSchema):
    """This schema represents a function call that was already generated."""
    agent_name: str = Field(description="The name of the agent that generated the function calls")
    function_name: str = Field(description="The name of the function")
    parameters: dict[str, str] = Field(description="The named parameters and their values")

class FunctionAgentInputSchema(BaseIOSchema):
    """
    This schema represents the input to the agent.
    The schema contains previously generated function calls, and the list of allowed generated functions.
    """
    user_input: str = Field(description="The chat message from the user", default="")
    functions_allowed_to_generate: list[FunctionSpecSchema] = Field(description="Definitions of the functions that this agent can generate")
    previously_generated_functions: list[FunctionCallSchema] = Field(description="Previously generated functions in this chat (some are from other agents)", default_factory=lambda: list)

class FunctionAgentOutputSchema(BaseIOSchema):
    """
    This schema represents the output of the agent.
    """
    chat_message: str = Field(description="The chat response to the user's message")
    generated_function_calls: list[FunctionCallSchema] = Field(description="The set of new generated function calls")
