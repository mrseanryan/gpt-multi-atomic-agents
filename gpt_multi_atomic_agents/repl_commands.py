from abc import ABC, abstractmethod
import os
from cornsnake import util_dir, util_file
from enum import StrEnum, auto
from typing import Text
from rich.console import Console

from .blackboard import Blackboard, FunctionCallBlackboard, GraphQLBlackboard
from .config import Config
from .util_print_agent import print_assistant_message_only

console = Console()


class CommandAction(StrEnum):
    no_action = auto()
    handled_already = auto()
    load_blackboard = auto()
    quit = auto()


class ReplCommandBase(ABC):
    @abstractmethod
    def get_name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def get_description(self) -> str:
        raise NotImplementedError

    def get_aliases(self) -> list[str]:
        return []

    @abstractmethod
    def do(self, blackboard: Blackboard, config: Config) -> CommandAction:
        raise NotImplementedError


class ClearReplCommand(ReplCommandBase):
    def get_name(self):
        return "clear"

    def get_aliases(self):
        return ["reset"]

    def get_description(self):
        return "Clear the blackboard, starting over."

    def do(self, blackboard: Blackboard, config: Config) -> CommandAction:
        blackboard.reset_all()
        console.print("(Blackboard has been reset)")
        return CommandAction.handled_already


class DumpReplCommand(ReplCommandBase):
    def get_name(self):
        return "dump"

    def get_aliases(self):
        return ["show"]

    def get_description(self):
        return "Dump the current blackboard state to the console"

    def do(self, blackboard: Blackboard, config: Config) -> CommandAction:
        console.print(blackboard)
        return CommandAction.handled_already


class HelpReplCommand(ReplCommandBase):
    def get_name(self):
        return "help"

    def get_description(self):
        return "Display help text"

    def do(self, blackboard: Blackboard, config: Config) -> CommandAction:
        print_help()
        return CommandAction.handled_already


class ListReplCommand(ReplCommandBase):
    def get_name(self):
        return "list"

    def get_description(self):
        return "List the local data files from previous blackboards"

    def do(self, blackboard: Blackboard, config: Config) -> CommandAction:
        files = util_dir.find_files_by_extension(
            dir_path=config.temp_data_dir_path, extension=".json"
        )
        files = [os.path.basename(f) for f in files]
        console.print(f"Blackboard data files: {files}")
        return CommandAction.handled_already


class LoadReplCommand(ReplCommandBase):
    def get_name(self):
        return "load"

    def get_description(self):
        return "Load a blackboard from the local data store"

    def do(self, blackboard: Blackboard, config: Config) -> CommandAction:
        return CommandAction.load_blackboard


def _get_bb_format(blackboard: Blackboard) -> str:
    if isinstance(blackboard, FunctionCallBlackboard):
        return "functioncall"
    elif isinstance(blackboard, GraphQLBlackboard):
        return "graphql"
    raise RuntimeError("Not a recognised kind of Blackboard")


class SaveReplCommand(ReplCommandBase):
    def get_name(self):
        return "save"

    def get_description(self):
        return "Save the blackboard to the local data store"

    def do(self, blackboard: Blackboard, config: Config) -> CommandAction:
        json_data = blackboard.model_dump_json()

        filename = input("Please enter a filename:")

        bb_format = _get_bb_format(blackboard=blackboard)

        filename = util_file.change_extension(filename, f".{bb_format}.json")
        filepath = os.path.join(config.temp_data_dir_path, filename)

        console.print(f"Saving blackboard to {filepath}")
        util_file.write_text_to_file(json_data, filepath)

        return CommandAction.handled_already


class QuitReplCommand(ReplCommandBase):
    def get_name(self):
        return "quit"

    def get_aliases(self):
        return ["bye", "exit", "stop"]

    def get_description(self):
        return "Exit the chat loop"

    def do(self, blackboard: Blackboard, config: Config) -> CommandAction:
        return CommandAction.quit


commands: list[ReplCommandBase] = [
    ClearReplCommand(),
    DumpReplCommand(),
    HelpReplCommand(),
    ListReplCommand(),
    LoadReplCommand(),
    SaveReplCommand(),
    QuitReplCommand(),
]
MIN_USER_PROMPT = 3


def _is_user_input_matching(user_prompt: str, aliases: list[str]) -> bool:
    return user_prompt.lower().strip() in aliases


def check_user_prompt(
    user_prompt: str, blackboard: Blackboard, config: Config
) -> CommandAction:
    user_prompt = user_prompt.strip()
    # special case:
    if not user_prompt or len(user_prompt) < MIN_USER_PROMPT:
        return HelpReplCommand().do(blackboard=blackboard, config=config)

    for command in commands:
        if _is_user_input_matching(
            user_prompt=user_prompt,
            aliases=command.get_aliases() + [command.get_name()],
        ):
            return command.do(blackboard=blackboard, config=config)
    return CommandAction.no_action


def print_help() -> None:
    print_assistant_message_only("Welcome to multi-agent chat")
    console.print(
        "Type in a question for the AI. If you are not sure what to type, then ask it a question like 'What can you do?'"
    )
    console.print("To exit, use the quit command")
    console.print("Available commands:")
    for command in commands:
        aliases = ", ".join(command.get_aliases())
        if aliases:
            aliases = f" (alias: {aliases})"
        console.print(
            Text(f"  {command.get_name()} - {command.get_description()}{aliases}")
        )
