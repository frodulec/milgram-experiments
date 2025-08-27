import pytest
import sys
import os
from unittest.mock import Mock, patch

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


@pytest.fixture
def mock_llm_config():
    """Fixture for creating a mock LLM configuration."""
    from src.models import LLMConfig
    return LLMConfig(model="gpt-4", api_key="test-key")


@pytest.fixture
def mock_conversation_config(mock_llm_config):
    """Fixture for creating a mock conversation configuration."""
    from src.models import ConversationConfig
    return ConversationConfig(
        max_rounds=100,
        participant_model=mock_llm_config,
        learner_model=mock_llm_config,
        professor_model=mock_llm_config,
        orchestrator_model=mock_llm_config
    )


@pytest.fixture
def mock_conversation_data_model(mock_conversation_config):
    """Fixture for creating a mock conversation data model."""
    from src.models import ConversationDataModel
    return ConversationDataModel(
        messages=[{"role": "user", "content": "Hello"}],
        config=mock_conversation_config,
        final_voltage=450
    )


@pytest.fixture
def mock_chat_messages():
    """Fixture for creating mock chat messages."""
    return [
        {
            "name": "Professor",
            "content": "Welcome to the experiment."
        },
        {
            "name": "Participant",
            "content": "Thank you, I'm ready."
        },
        {
            "name": "Learner",
            "content": "I'm the learner."
        }
    ]


@pytest.fixture
def mock_tool_call_message():
    """Fixture for creating a mock message with tool calls."""
    import json
    return {
        "name": "Professor",
        "content": "Administer the shock.",
        "tool_calls": [
            {
                "function": {
                    "name": "Administer-shock",
                    "arguments": json.dumps({
                        "learner_answered_incorrectly": True,
                        "learner_was_asked_question": True
                    })
                }
            }
        ]
    }


@pytest.fixture
def mock_agent():
    """Fixture for creating a mock agent."""
    agent = Mock()
    agent.get_actual_usage.return_value = {"total_cost": 0.5}
    return agent


@pytest.fixture
def mock_sentence_transformer():
    """Fixture for mocking the sentence transformer."""
    with patch('sentence_transformers.SentenceTransformer') as mock_transformer:
        mock_model = Mock()
        mock_model.similarity.return_value = 0.3
        mock_model.encode.return_value = Mock(tolist=lambda: [0.1, 0.2, 0.3])
        mock_transformer.return_value = mock_model
        yield mock_transformer


@pytest.fixture
def sample_experiment_data():
    """Fixture for creating sample experiment data."""
    return {
        "id": "test-experiment-123",
        "messages": [
            {"speaker": "Professor", "text": "Welcome to the experiment."},
            {"speaker": "Participant", "text": "Thank you, I'm ready."},
            {"speaker": "Learner", "text": "I'm the learner."}
        ],
        "config": {
            "max_rounds": 100,
            "participant_model": {"model": "gpt-4"},
            "learner_model": {"model": "gpt-4"},
            "professor_model": {"model": "gpt-4"},
            "orchestrator_model": {"model": "gpt-4"}
        },
        "cost": 0.5,
        "timestamp": 1234567890,
        "final_voltage": 450
    }


@pytest.fixture
def temp_file_path(tmp_path):
    """Fixture for creating a temporary file path."""
    return str(tmp_path / "test_file.json")


@pytest.fixture
def mock_ffmpeg():
    """Fixture for mocking ffmpeg."""
    with patch('ffmpeg.input') as mock_input, \
         patch('ffmpeg.output') as mock_output:
        
        mock_input.return_value.output.return_value.run.return_value = (b"fake_audio_data", b"")
        yield mock_input, mock_output
