import logging
from cornsnake import util_list, util_string

logger = logging.getLogger(__file__)


def _clean_mutation_name(name):
    return util_string.filter_string_via_regex(name, "^[a-zA-Z0-9_]+$", "")


def parse_out_mutation_names_from_schemas(
    accepted_graphql_schemas: list[str],
) -> list[str]:
    accepted_mutation_names = []

    for accepted in accepted_graphql_schemas:
        token = "type Mutation {"
        if token not in accepted:
            continue
        parts = accepted.split(token)
        if len(parts) != 2:
            logger.warning("Expected 2 parts in accepted mutations schema")
            continue
        mutation_def = parts[1].split("}")[0]
        mutation = mutation_def.split("(")[0].strip()
        if mutation:
            accepted_mutation_names.append(_clean_mutation_name(mutation))

    return accepted_mutation_names


def filter_to_matching_mutation_calls(
    previously_generated_mutation_calls: list[str], accepted_mutation_names: list[str]
) -> list[str]:
    accepted_mutation_names__adjusted = util_list.flatten(
        [[f"{n}(", f"{n} ("] for n in accepted_mutation_names]
    )

    matching: list[str] = []
    for previous in previously_generated_mutation_calls:
        if any(
            list(filter(lambda a: a in previous, accepted_mutation_names__adjusted))
        ):
            matching.append(previous)

    return matching
