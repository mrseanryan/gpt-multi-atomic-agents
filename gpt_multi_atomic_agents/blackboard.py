from dataclasses import dataclass, field

from .functions_dto import FunctionCallSchema

@dataclass
class Blackboard:
    previously_generated_functions: list[FunctionCallSchema] = field(default_factory=list)

    def add_generated_functions(self, generated_function_calls: list[FunctionCallSchema]) -> None:
        self.previously_generated_functions += generated_function_calls

    def get_generated_functions_matching(self, function_names: list[str]) -> list[FunctionCallSchema]:
        return list(filter(lambda f: f.function_name in function_names, self.previously_generated_functions))
