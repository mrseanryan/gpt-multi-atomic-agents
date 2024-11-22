from dataclasses import dataclass, field
import logging

from .functions_dto import FunctionCallSchema

logger = logging.getLogger("functions_expert")

@dataclass
class Blackboard:
    # TODO try split this blackboard, have a base class
    previously_generated_functions: list[FunctionCallSchema] = field(default_factory=list)
    previously_generated_mutation_calls: list[str] = field(default_factory=list)

    def add_generated_functions(self, generated_function_calls: list[FunctionCallSchema]) -> None:
        self.previously_generated_functions += generated_function_calls

    def get_generated_functions_matching(self, function_names: list[str]) -> list[FunctionCallSchema]:
        return list(filter(lambda f: f.function_name in function_names, self.previously_generated_functions))

    def add_generated_mutations(self, generated_mutation_calls: list[str]) -> None:
        self.previously_generated_mutation_calls.append(generated_mutation_calls)

    def get_generated_mutations_matching(self, accepted_graphql_schemas: list[str]) -> list[str]:
        accepted_mutation_names = []

        # TODO unit test me
        for accepted in accepted_graphql_schemas:
            token = "type Mutation {"
            if token not in accepted:
                continue
            parts = accepted.split(token)
            if len(parts) != 2:
                logger.warning("Expected 2 parts in accepted mutations schema")
                continue
            mutation_defs = parts[1].split("}")[0]
            for mutation_line in mutation_defs.splitlines():
                if mutation_line:
                    mutation = mutation_line.split("(")[0].strip()
                    accepted_mutation_names.append(mutation)

        matching:list[str] = []
        for previous in self.previously_generated_mutation_calls:
            if any( list(filter(lambda a: a in previous, accepted_mutation_names))):
                matching.append(previous)

        return matching
