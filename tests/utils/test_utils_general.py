import pytest
import os
import json
import tempfile
from unittest.mock import patch, mock_open
from src.utils.general import get_provider_name, load_experiments


class TestGetProviderName:
    """Test the get_provider_name function for different model configurations."""
    
    def test_openai_gpt5_models(self):
        """Test OpenAI GPT-5 model detection."""
        assert get_provider_name("gpt-5") == "OpenAI - GPT-5"
        assert get_provider_name("gpt-5-turbo") == "OpenAI - GPT-5"
        assert get_provider_name("GPT-5-PREVIEW") == "OpenAI - GPT-5"
    
    def test_openai_pre_gpt5_models(self):
        """Test OpenAI pre-GPT-5 model detection."""
        assert get_provider_name("gpt-4") == "OpenAI pre-GPT 5"
        assert get_provider_name("gpt-3.5-turbo") == "OpenAI pre-GPT 5"
        assert get_provider_name("gpt-4-turbo") == "OpenAI pre-GPT 5"
    
    def test_anthropic_models(self):
        """Test Anthropic model detection."""
        assert get_provider_name("claude-3") == "Anthropic"
        assert get_provider_name("claude-3-opus") == "Anthropic"
        assert get_provider_name("claude-2") == "Anthropic"
    
    def test_google_models(self):
        """Test Google model detection."""
        assert get_provider_name("gemini-pro") == "Google"
        assert get_provider_name("gemini-ultra") == "Google"
        assert get_provider_name("gemini-flash") == "Google"
    
    def test_moonshot_models(self):
        """Test Moonshot AI model detection."""
        assert get_provider_name("kimi") == "Moonshot AI"
        assert get_provider_name("kimi-pro") == "Moonshot AI"
        assert get_provider_name("kimi-ultra") == "Moonshot AI"
    
    def test_xai_models(self):
        """Test xAI model detection."""
        assert get_provider_name("grok") == "xAI"
        assert get_provider_name("grok-beta") == "xAI"
        assert get_provider_name("grok-pro") == "xAI"
    
    def test_alibaba_models(self):
        """Test Alibaba model detection."""
        assert get_provider_name("qwen") == "Alibaba"
        assert get_provider_name("qwen-turbo") == "Alibaba"
        assert get_provider_name("qwen-plus") == "Alibaba"
    
    def test_unknown_models(self):
        """Test unknown model detection."""
        assert get_provider_name("unknown-model") == "Unknown"
        assert get_provider_name("custom-model") == "Unknown"
        assert get_provider_name("") == "Unknown"
    
    def test_case_insensitive(self):
        """Test that model detection is case insensitive."""
        assert get_provider_name("GPT-4") == "OpenAI pre-GPT 5"
        assert get_provider_name("CLAUDE-3") == "Anthropic"
        assert get_provider_name("GEMINI-PRO") == "Google"


class TestLoadExperiments:
    """Test the load_experiments function."""
    
    def test_load_experiments_nonexistent_folder(self):
        """Test loading experiments from a non-existent folder."""
        with patch('os.path.exists', return_value=False):
            experiments = load_experiments(folder="nonexistent")
            assert experiments == []
    
    def test_load_experiments_empty_folder(self):
        """Test loading experiments from an empty folder."""
        with patch('os.path.exists', return_value=True), \
             patch('os.listdir', return_value=[]):
            experiments = load_experiments(folder="empty_folder")
            assert experiments == []
    
    def test_load_experiments_valid_files(self):
        """Test loading experiments from valid JSON files."""
        mock_files = [
            "experiment_123.json",
            "experiment_456.json"
        ]
        
        mock_data1 = {
            "id": "123",
            "messages": [
                {"speaker": "Participant", "text": "Hello"},
                {"speaker": "Learner", "text": "Hi"}
            ]
        }
        
        mock_data2 = {
            "id": "456", 
            "messages": [
                {"speaker": "Participant", "text": "Test"},
                {"speaker": "Orchestrator", "text": "Admin message"}
            ]
        }
        
        with patch('os.path.exists', return_value=True), \
             patch('os.listdir', return_value=mock_files), \
             patch('builtins.open', mock_open()), \
             patch('json.load') as mock_json_load:
            
            mock_json_load.side_effect = [mock_data1, mock_data2]
            
            experiments = load_experiments(folder="test_folder")
            
            assert len(experiments) == 2
            assert experiments[0]["id"] == "123"
            assert experiments[0]["filename"] == "experiment_123.json"
            assert experiments[1]["id"] == "456"
            assert experiments[1]["filename"] == "experiment_456.json"
    
    def test_load_experiments_skip_orchestrator(self):
        """Test loading experiments with orchestrator messages filtered out."""
        mock_files = ["experiment_123.json"]
        
        mock_data = {
            "id": "123",
            "messages": [
                {"speaker": "Participant", "text": "Hello"},
                {"speaker": "Orchestrator", "text": "Admin message"},
                {"speaker": "Learner", "text": "Hi"}
            ]
        }
        
        with patch('os.path.exists', return_value=True), \
             patch('os.listdir', return_value=mock_files), \
             patch('builtins.open', mock_open()), \
             patch('json.load', return_value=mock_data):
            
            experiments = load_experiments(skip_orchestrator=True, folder="test_folder")
            
            assert len(experiments) == 1
            assert len(experiments[0]["messages"]) == 2
            assert experiments[0]["messages"][0]["speaker"] == "Participant"
            assert experiments[0]["messages"][1]["speaker"] == "Learner"
    
    def test_load_experiments_invalid_files(self):
        """Test loading experiments with invalid JSON files."""
        mock_files = [
            "experiment_123.json",
            "not_an_experiment.txt",
            "experiment_456.json"
        ]
        
        mock_data = {"id": "123", "messages": []}
        
        with patch('os.path.exists', return_value=True), \
             patch('os.listdir', return_value=mock_files), \
             patch('builtins.open', mock_open()), \
             patch('json.load', return_value=mock_data):
            
            experiments = load_experiments(folder="test_folder")
            
            # Should only load files that start with "experiment_" and end with ".json"
            assert len(experiments) == 2
    
    def test_load_experiments_json_error(self):
        """Test loading experiments when JSON parsing fails."""
        mock_files = ["experiment_123.json"]
        
        with patch('os.path.exists', return_value=True), \
             patch('os.listdir', return_value=mock_files), \
             patch('builtins.open', mock_open()), \
             patch('json.load', side_effect=json.JSONDecodeError("Invalid JSON", "", 0)):
            
            experiments = load_experiments(folder="test_folder")
            
            # Should handle JSON errors gracefully and return empty list
            assert experiments == []
    
    def test_load_experiments_file_error(self):
        """Test loading experiments when file reading fails."""
        mock_files = ["experiment_123.json"]
        
        with patch('os.path.exists', return_value=True), \
             patch('os.listdir', return_value=mock_files), \
             patch('builtins.open', side_effect=FileNotFoundError("File not found")):
            
            experiments = load_experiments(folder="test_folder")
            
            # Should handle file errors gracefully and return empty list
            assert experiments == []
