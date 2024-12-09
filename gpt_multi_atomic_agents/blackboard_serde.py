import os
import logging
from cornsnake import util_dir, util_file, util_json

from pydantic import TypeAdapter
from rich.console import Console
from rich.text import Text

from .blackboard import Blackboard
from .util_pydantic import CustomBaseModel

from .config import Config

console = Console()
logger = logging.getLogger(__file__)


class SerializedBlackboard(CustomBaseModel):
    blackboard: Blackboard
    file_schema_version: str = "0.2"


def load_blackboard_from_file(
    config: Config, existing_blackboard: Blackboard
) -> Blackboard | None:
    filename = input("Please enter a filename:")
    filepath = os.path.join(config.temp_data_dir_path, filename)

    if not os.path.exists(filepath):
        console.print(
            Text(
                "That file does not exist. Please use the list command to view the current files."
            ),
            style="red",
        )
        return existing_blackboard

    console.print(f"Loading blackboard from {filepath}")
    try:
        json_data = util_json.read_from_json_file(filepath)
        serialized = TypeAdapter(SerializedBlackboard).validate_python(json_data)
        return serialized.blackboard
    except Exception as e:
        logger.exception(e)

    console.print(
        Text(
            "Could not load that blackboard (the file could be old or a different format: FunctionCalling vs GraphQL)"
        ),
        style="red",
    )
    return None


def save_blackboard_to_file(blackboard: Blackboard, filename: str, config: Config):
    filename = util_file.change_extension(filename, f".{blackboard.format.value}.json")
    filepath = os.path.join(config.temp_data_dir_path, filename)

    console.print(f"Saving blackboard to {filepath}")

    serialized = SerializedBlackboard(format=blackboard.format, blackboard=blackboard)
    json_data = serialized.model_dump_json()

    util_file.write_text_to_file(json_data, filepath)


def list_blackboard_files(blackboard: Blackboard, config: Config):
    files = util_dir.find_files_by_extension(
        dir_path=config.temp_data_dir_path, extension=f"{blackboard.format.value}.json"
    )
    files = [os.path.basename(f) for f in files]
    console.print(f"Blackboard data files: {files}")
