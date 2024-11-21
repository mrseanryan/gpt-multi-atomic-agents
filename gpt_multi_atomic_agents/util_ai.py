import instructor


from rich.console import Console
from rich.text import Text
from anthropic import AnthropicBedrock
from groq import Groq
from openai import OpenAI

from . import config

console = Console()

def create_client():
    client: instructor.Instructor|None = None
    model: str|None = None
    max_tokens: int|None = None
    match(config.AI_PLATFORM):
        case config.AI_PLATFORM_Enum.groq:
            client = instructor.from_groq(Groq())
            model = config.GROQ_MODEL
        case config.AI_PLATFORM_Enum.openai:
            client = instructor.from_openai(OpenAI())
            model = config.OPEN_AI_MODEL
        case config.AI_PLATFORM_Enum.bedrock_anthropic:
            client = instructor.from_anthropic(AnthropicBedrock())
            model = config.ANTHROPIC_MODEL
            max_tokens = config.ANTHROPIC_MAX_TOKENS
        case _:
            raise RuntimeError(f"Not a recognised AI_PLATFORM: '{config.AI_PLATFORM}' - please check config.py.")

    console.print(Text(f"  AI platform: {config.AI_PLATFORM.value}", style="magenta"))

    return client, model, max_tokens
