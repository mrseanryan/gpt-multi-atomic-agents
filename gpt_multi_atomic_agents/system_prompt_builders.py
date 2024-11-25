from abc import ABC, abstractmethod
from dataclasses import dataclass
from atomic_agents.lib.components.system_prompt_generator import SystemPromptGenerator

from . import prompts_agent_functions, prompts_agent_graphql
from .config import Config
from .functions_dto import FunctionSpecSchema


@dataclass
class SystemPromptBuilderBase(ABC):
    _config: Config

    @abstractmethod
    def build_system_prompt(self) -> str:
        raise NotImplementedError


@dataclass
class FunctionSystemPromptBuilder(SystemPromptBuilderBase):
    allowed_functions_to_generate: list[FunctionSpecSchema]
    topics: list[str]

    def build_system_prompt(self) -> str:
        allowed_functions_to_generate_names = [
            f.function_name for f in self.allowed_functions_to_generate
        ]

        return SystemPromptGenerator(
            background=[
                "You are a helpful assistant that can only generate function calls using the provided definitions."
            ],
            steps=[
                # TODO: could break the prompt down into steps
                prompts_agent_functions.build_agent_prompt(
                    allowed_functions_to_generate_names,
                    topics=self.topics,
                    _config=self._config,
                )
            ],
            output_instructions=[
                "Your output should always be a set of zero or more generated functions, using only the allowed function definitions."
            ],
        )


@dataclass
class GraphQLSystemPromptBuilder(SystemPromptBuilderBase):
    def build_system_prompt(self) -> str:
        return SystemPromptGenerator(
            background=[
                "You are a helpful assistant that can only generates GraphQL mutations using the provided definitions."
            ],
            steps=[
                # TODO: could break the prompt down into steps
                prompts_agent_graphql.build_agent_prompt()
            ],
            output_instructions=[
                # TODO: add also output GraphQL queries
                "Your output should always be a set of zero or more GraphQL mutation calls, using only the allowed GraphQL mutations definitions."
            ],
        )
