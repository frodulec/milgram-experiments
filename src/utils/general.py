import logging
import os
import json
from typing import List, Dict



logger = logging.getLogger(__name__)


def get_provider_name(model_name: str) -> str:
    """
    Returns the provider name for a given model configuration.
    
    Args:
        model_config: str
    
    Returns:
        The provider name as a string, or None if provider not found
    """
    model_name = model_name.lower()
    if "gpt-5" in model_name:
        return "OpenAI - GPT-5"
    elif "gpt-" in model_name:
        return "OpenAI pre-GPT 5"
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
    
    logger.info(f"Unknown provider for model: {model_name}")
    return "Unknown"


def load_experiments(skip_orchestrator: bool = False, folder: str = "results") -> List[Dict]:
    """Load all experiment results from the results directory."""
    experiments = []
    
    # Check if results directory exists
    if not os.path.exists(folder):
        return []
    
    # Iterate through all json files in the results directory, without subfolders
    for filename in os.listdir(folder):
        if filename.startswith("experiment_") and filename.endswith(".json"):
            try:
                with open(os.path.join(folder, filename), "r") as f:
                    data = json.load(f)
                    data["filename"] = filename  # Add filename for reference
                    data["messages"] = [msg for msg in data["messages"] if msg["speaker"] != "Orchestrator"] if skip_orchestrator else data["messages"]
                    experiments.append(data)
            except Exception as e:
                logger.error(f"Error reading file {filename}: {e}")
    
    logger.info(f"Loaded {len(experiments)} experiments")
    return experiments