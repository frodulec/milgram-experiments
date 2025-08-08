


def get_provider_name(model_name: str) -> str:
    """
    Returns the provider name for a given model configuration.
    
    Args:
        model_config: str
    
    Returns:
        The provider name as a string, or None if provider not found
    """
    model_name = model_name.lower()
    if "gpt-" in model_name:
        return "OpenAI"
    elif model_name.startswith("claude-"):
        return "Anthropic"
    elif model_name.startswith("gemini-"):
        return "Google"
    elif "kimi" in model_name:
        return "Moonshot AI"
    elif "grok" in model_name:
        return "xAI"
    elif "qwen" in model_name:
        return "Alibaba"
    
    return "Unknown"