from models import LLMConfig
import os
from dotenv import load_dotenv



load_dotenv()


class GPT_4_1(LLMConfig):
    model: str = "gpt-4.1-2025-04-14"
    api_key: str = os.environ["OPENAI_API_KEY"]


class GPT_4_1_nano(LLMConfig):
    model: str = "gpt-4.1-nano-2025-04-14"
    api_key: str = os.environ["OPENAI_API_KEY"]


class GPT_4o(LLMConfig):
    model: str = "gpt-4o"
    api_key: str = os.environ["OPENAI_API_KEY"]

class GPT_4o_mini(LLMConfig):
    model: str = "gpt-4o-mini"
    api_key: str = os.environ["OPENAI_API_KEY"]


class ClaudeSonnet4(LLMConfig):
    model: str = "claude-sonnet-4-20250514"
    api_key: str = os.environ["ANTHROPIC_API_KEY"]


class ClaudeHaiku(LLMConfig):
    model: str = "claude-3-5-haiku-20241022"
    api_key: str = os.environ["ANTHROPIC_API_KEY"]


class ClaudeSonnet3_7(LLMConfig):
    model: str = "claude-3-7-sonnet-2025021"
    api_key: str = os.environ["ANTHROPIC_API_KEY"]


class Gemini2_5_Pro_preview(LLMConfig):
    model: str = "gemini-2.5-pro-preview-06-05"
    api_key: str = os.environ["GOOGLE_API_KEY"]


class Gemini2_5_Flash_preview(LLMConfig):
    model: str = "gemini-2.5-flash-preview-05-20"
    api_key: str = os.environ["GOOGLE_API_KEY"]


class Gemini2_0_Flash(LLMConfig):
    model: str = "gemini-2.0-flash"
    api_key: str = os.environ["GOOGLE_API_KEY"]
