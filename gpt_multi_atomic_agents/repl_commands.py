from abc import ABC, abstractmethod
from enum import StrEnum, auto
from typing import Text
from rich.console import Console
from .blackboard import Blackboard
from .util_print_agent import print_assistant_message_only

console = Console()


class CommandAction(StrEnum):
    no_action = auto()
    handled_already = auto()
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
    def do(self, blackboard: Blackboard) -> CommandAction:
        raise NotImplementedError


class ClearReplCommand(ReplCommandBase):
    def get_name(self):
        return "clear"

    def get_aliases(self):
        return ["reset"]

    def get_description(self):
        return "Clear the blackboard, starting over."

    def do(self, blackboard: Blackboard) -> CommandAction:
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

    def do(self, blackboard: Blackboard) -> CommandAction:
        console.print(blackboard)
        return CommandAction.handled_already


class HelpReplCommand(ReplCommandBase):
    def get_name(self):
        return "help"

    def get_description(self):
        return "Display help text"

    def do(self, blackboard: Blackboard) -> CommandAction:
        print_help()
        return CommandAction.handled_already


class QuitReplCommand(ReplCommandBase):
    def get_name(self):
        return "quit"

    def get_aliases(self):
        return ["bye", "exit", "stop"]

    def get_description(self):
        return "Exit the chat loop"

    def do(self, blackboard: Blackboard) -> CommandAction:
        return CommandAction.quit


commands: list[ReplCommandBase] = [
    ClearReplCommand(),
    DumpReplCommand(),
    HelpReplCommand(),
    QuitReplCommand(),
]
MIN_USER_PROMPT = 3


def _is_user_input_matching(user_prompt: str, aliases: list[str]) -> bool:
    return user_prompt.lower().strip() in aliases


def check_user_prompt(user_prompt: str, blackboard: Blackboard) -> CommandAction:
    user_prompt = user_prompt.strip()
    # special case:
    if not user_prompt or len(user_prompt) < MIN_USER_PROMPT:
        return HelpReplCommand().do(blackboard=blackboard)

    for command in commands:
        if _is_user_input_matching(
            user_prompt=user_prompt,
            aliases=command.get_aliases() + [command.get_name()],
        ):
            return command.do(blackboard=blackboard)
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


# save X - saves to filename

# list - lists files in the configured save location

# load X - loads from filename
