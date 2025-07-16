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
    api_type: str = "anthropic"


class ClaudeHaiku(LLMConfig):
    model: str = "claude-3-5-haiku-20241022"
    api_key: str = os.environ["ANTHROPIC_API_KEY"]
    api_type: str = "anthropic"


class ClaudeSonnet3_7(LLMConfig):
    model: str = "claude-3-7-sonnet-20250219"
    api_key: str = os.environ["ANTHROPIC_API_KEY"]
    api_type: str = "anthropic"


class Gemini2_5Pro(LLMConfig):
    model: str = "gemini-2.5-pro"
    api_key: str = os.environ["GOOGLE_API_KEY"]
    api_type: str = "google"


class Gemini2_5Flash(LLMConfig):
    model: str = "gemini-2.5-flash"
    api_key: str = os.environ["GOOGLE_API_KEY"]
    api_type: str = "google"


class Gemini2_5FlashLite(LLMConfig):
    model: str = "gemini-2.5-flash-lite-preview-06-17"
    api_key: str = os.environ["GOOGLE_API_KEY"]
    api_type: str = "google"


class KimiK2(LLMConfig):
    model: str = "moonshotai/kimi-k2"
    api_key: str = os.environ["OPENROUTER_API_KEY"]
    base_url: str = "https://openrouter.ai/api/v1"


class Grok4(LLMConfig):
    model: str = "x-ai/grok-4"
    api_key: str = os.environ["OPENROUTER_API_KEY"]
    base_url: str = "https://openrouter.ai/api/v1"