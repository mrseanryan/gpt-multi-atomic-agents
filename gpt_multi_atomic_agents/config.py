import logging
import os
from cornsnake import util_toml
from dataclasses import dataclass
from enum import StrEnum, auto

logger = logging.getLogger(__file__)


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
    ai_platform: AI_PLATFORM_Enum = AI_PLATFORM_Enum.bedrock_anthropic
    model: str = ANTHROPIC_MODEL
    max_tokens: int = ANTHROPIC_MAX_TOKENS
    is_debug: bool = False
    delay_between_calls_in_seconds: float = 0.0
    temp_data_dir_path: str = "data-generated"


def _get_path_to_ini(path_to_ini: str) -> str:
    path_to_ini = path_to_ini
    if not os.path.exists(path_to_ini):
        # look in current directory
        path_to_ini = os.path.join(os.getcwd(), path_to_ini)
    logger.info(f"Reading config from '{path_to_ini}'")
    return path_to_ini


def load_config(path_to_ini: str) -> Config:
    path_to_file = _get_path_to_ini(path_to_ini)
    config = Config
    util_toml.read_config_ini_file(path_to_file=path_to_file, config_object=config)
    return config
