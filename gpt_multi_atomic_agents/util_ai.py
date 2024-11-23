import instructor
from rich.console import Console
from rich.text import Text
from anthropic import AnthropicBedrock
from groq import Groq
from openai import OpenAI

from . import config

console = Console()


def create_client(_config: config.Config):
    client: instructor.Instructor | None = None
    model: str | None = None
    max_tokens: int | None = None
    match _config.ai_platform:
        case config.AI_PLATFORM_Enum.groq:
            client = instructor.from_groq(Groq())
            model = _config.model
        case config.AI_PLATFORM_Enum.openai:
            client = instructor.from_openai(OpenAI())
            model = _config.model
        case config.AI_PLATFORM_Enum.bedrock_anthropic:
            client = instructor.from_anthropic(AnthropicBedrock())
            model = _config.model
            max_tokens = _config.max_tokens
        case _:
            raise RuntimeError(
                f"Not a recognised AI_PLATFORM: '{_config.ai_platform}' - please check Config."
            )

    console.print(Text(f"  AI platform: {_config.ai_platform}", style="magenta"))

    return client, model, max_tokens
