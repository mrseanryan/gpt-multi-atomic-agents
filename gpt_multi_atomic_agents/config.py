from dataclasses import dataclass
from enum import StrEnum, auto

class AI_PLATFORM_Enum(StrEnum):
    openai = auto()
    groq = auto()
    bedrock_anthropic = auto()

GROQ_MODEL = "llama-3.1-70b-versatile"  # 'llama-3.1-70b-versatile' #"llama-3.1-8b-instant"  #  llama3-8b-8192

OPEN_AI_MODEL = "gpt-4o"  # "gpt-3.5-turbo"

ANTHROPIC_MODEL = "anthropic.claude-3-5-sonnet-20240620-v1:0"
ANTHROPIC_MAX_TOKENS = 8192

@dataclass
class Config:
    ai_platform: AI_PLATFORM_Enum
    model: str
    max_tokens: int
    is_debug: bool = False
