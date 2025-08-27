import pytest
from datetime import datetime
from src.models import (
    LLMConfig, 
    Roles, 
    ConversationConfig, 
    ConversationDataModel
)
from src.utils.general import remove_api_keys_from_json


class TestLLMConfig:
    def test_llm_config_creation(self):
        """Test LLMConfig creation with required and optional fields."""
        config = LLMConfig(model="gpt-4", api_key="test-key")
        assert config.model == "gpt-4"
        assert config.api_key == "test-key"
    
    def test_llm_config_without_api_key(self):
        """Test LLMConfig creation without API key."""
        config = LLMConfig(model="gpt-4")
        assert config.model == "gpt-4"
        assert config.api_key is None


class TestRoles:
    def test_roles_enum_values(self):
        """Test that all expected roles exist in the enum."""
        assert Roles.PROFESSOR.value == "Professor"
        assert Roles.PARTICIPANT.value == "Participant"
        assert Roles.LEARNER.value == "Learner"
        assert Roles.ORCHESTRATOR.value == "Orchestrator"
    
    def test_roles_enum_membership(self):
        """Test that roles can be accessed by value."""
        assert "Professor" in [role.value for role in Roles]
        assert "Participant" in [role.value for role in Roles]
        assert "Learner" in [role.value for role in Roles]
        assert "Orchestrator" in [role.value for role in Roles]


class TestConversationConfig:
    def test_conversation_config_defaults(self):
        """Test ConversationConfig with default values."""
        config = ConversationConfig(
            participant_model=LLMConfig(model="gpt-4"),
            learner_model=LLMConfig(model="gpt-4"),
            professor_model=LLMConfig(model="gpt-4"),
            orchestrator_model=LLMConfig(model="gpt-4")
        )
        assert config.max_rounds == 400
        assert config.participant_model.model == "gpt-4"
        assert config.learner_model.model == "gpt-4"
        assert config.professor_model.model == "gpt-4"
        assert config.orchestrator_model.model == "gpt-4"
    
    def test_conversation_config_custom_max_rounds(self):
        """Test ConversationConfig with custom max_rounds."""
        config = ConversationConfig(
            max_rounds=100,
            participant_model=LLMConfig(model="gpt-4"),
            learner_model=LLMConfig(model="gpt-4"),
            professor_model=LLMConfig(model="gpt-4"),
            orchestrator_model=LLMConfig(model="gpt-4")
        )
        assert config.max_rounds == 100


class TestConversationDataModel:
    def test_conversation_data_model_creation(self):
        """Test ConversationDataModel creation with all required fields."""
        config = ConversationConfig(
            participant_model=LLMConfig(model="gpt-4"),
            learner_model=LLMConfig(model="gpt-4"),
            professor_model=LLMConfig(model="gpt-4"),
            orchestrator_model=LLMConfig(model="gpt-4")
        )
        
        model = ConversationDataModel(
            messages=[{"role": "user", "content": "Hello"}],
            config=config,
            final_voltage=450
        )
        
        assert model.messages == [{"role": "user", "content": "Hello"}]
        assert model.config == config
        assert model.final_voltage == 450
        assert model.cost == 0.0
        assert isinstance(model.id, str)
        assert isinstance(model.timestamp, int)
    
    def test_conversation_data_model_defaults(self):
        """Test ConversationDataModel with default values."""
        config = ConversationConfig(
            participant_model=LLMConfig(model="gpt-4"),
            learner_model=LLMConfig(model="gpt-4"),
            professor_model=LLMConfig(model="gpt-4"),
            orchestrator_model=LLMConfig(model="gpt-4")
        )
        
        model = ConversationDataModel(
            messages=[],
            config=config,
            final_voltage=0
        )
        
        assert model.cost == 0.0
        assert isinstance(model.id, str)
        assert isinstance(model.timestamp, int)
        assert model.timestamp > 0
    
    def test_conversation_data_model_dump_removes_api_keys(self):
        """Test that model_dump removes API keys from config."""
        config = ConversationConfig(
            participant_model=LLMConfig(model="gpt-4", api_key="key1"),
            learner_model=LLMConfig(model="gpt-4", api_key="key2"),
            professor_model=LLMConfig(model="gpt-4", api_key="key3"),
            orchestrator_model=LLMConfig(model="gpt-4", api_key="key4")
        )
        
        model = ConversationDataModel(
            messages=[],
            config=config,
            final_voltage=0
        )
        
        dumped = model.model_dump()
        
        # Check that API keys are removed
        assert dumped["config"]["participant_model"].get("api_key") is None
        assert dumped["config"]["learner_model"].get("api_key") is None
        assert dumped["config"]["professor_model"].get("api_key") is None
        assert dumped["config"]["orchestrator_model"].get("api_key") is None
        
        # Check that other fields are preserved
        assert dumped["config"]["participant_model"]["model"] == "gpt-4"
        assert dumped["config"]["learner_model"]["model"] == "gpt-4"
        assert dumped["config"]["professor_model"]["model"] == "gpt-4"
        assert dumped["config"]["orchestrator_model"]["model"] == "gpt-4"


class TestRemoveApiKeysFromJson:
    def test_remove_api_keys_from_json(self):
        """Test the remove_api_keys_from_json utility function."""
        data = {
            "config": {
                "participant_model": {"model": "gpt-4", "api_key": "key1"},
                "learner_model": {"model": "gpt-4", "api_key": "key2"},
                "professor_model": {"model": "gpt-4", "api_key": "key3"},
                "orchestrator_model": {"model": "gpt-4", "api_key": "key4"}
            },
            "other_field": "value"
        }
        
        result = remove_api_keys_from_json(data)
        
        # Check that API keys are removed
        assert result["config"]["participant_model"].get("api_key") is None
        assert result["config"]["learner_model"].get("api_key") is None
        assert result["config"]["professor_model"].get("api_key") is None
        assert result["config"]["orchestrator_model"].get("api_key") is None
        
        # Check that other fields are preserved
        assert result["config"]["participant_model"]["model"] == "gpt-4"
        assert result["other_field"] == "value"
    
    def test_remove_api_keys_from_json_missing_keys(self):
        """Test remove_api_keys_from_json when API keys are already missing."""
        data = {
            "config": {
                "participant_model": {"model": "gpt-4"},
                "learner_model": {"model": "gpt-4"},
                "professor_model": {"model": "gpt-4"},
                "orchestrator_model": {"model": "gpt-4"}
            }
        }
        
        result = remove_api_keys_from_json(data)
        
        # Should not raise an error and should preserve the data
        assert result == data
