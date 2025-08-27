import pytest
import json
from unittest.mock import Mock, patch, mock_open
from src.utils.chat_utils import (
    check_termination,
    agents_total_cost,
    find_last_administered_shock,
    check_if_administered_shock,
    convert_chat_history_to_json,
    load_conversation_dictionary
)
from src.models import Roles


class TestCheckTermination:
    """Test the check_termination function."""
    
    def test_termination_with_goodbye(self):
        """Test that messages containing 'goodbye' are detected as termination."""
        message = {"content": "Goodbye, thank you for participating!"}
        assert check_termination(message) is True
    
    def test_termination_with_goodbye_case_insensitive(self):
        """Test that 'goodbye' detection is case insensitive."""
        message = {"content": "GOODBYE everyone!"}
        assert check_termination(message) is True
    
    def test_no_termination_without_goodbye(self):
        """Test that messages without 'goodbye' are not detected as termination."""
        message = {"content": "Hello, how are you?"}
        assert check_termination(message) is False
    
    def test_termination_with_empty_content(self):
        """Test that empty content is not detected as termination."""
        message = {"content": ""}
        assert check_termination(message) is False
    
    def test_termination_with_none_content(self):
        """Test that None content is not detected as termination."""
        message = {"content": None}
        assert check_termination(message) is False


class TestAgentsTotalCost:
    """Test the agents_total_cost function."""
    
    def test_agents_total_cost_with_costs(self):
        """Test calculating total cost from multiple agents."""
        agent1 = Mock()
        agent1.get_actual_usage.return_value = {"total_cost": 0.5}
        
        agent2 = Mock()
        agent2.get_actual_usage.return_value = {"total_cost": 0.3}
        
        agent3 = Mock()
        agent3.get_actual_usage.return_value = {"total_cost": 0.2}
        
        agents = [agent1, agent2, agent3]
        total_cost = agents_total_cost(agents)
        
        assert total_cost == 1.0
    
    def test_agents_total_cost_with_no_usage(self):
        """Test calculating total cost when agents have no usage data."""
        agent1 = Mock()
        agent1.get_actual_usage.return_value = None
        
        agent2 = Mock()
        agent2.get_actual_usage.return_value = None
        
        agents = [agent1, agent2]
        total_cost = agents_total_cost(agents)
        
        assert total_cost == 0.0
    
    def test_agents_total_cost_mixed_usage(self):
        """Test calculating total cost with mixed usage data."""
        agent1 = Mock()
        agent1.get_actual_usage.return_value = {"total_cost": 0.5}
        
        agent2 = Mock()
        agent2.get_actual_usage.return_value = None
        
        agent3 = Mock()
        agent3.get_actual_usage.return_value = {"total_cost": 0.3}
        
        agents = [agent1, agent2, agent3]
        total_cost = agents_total_cost(agents)
        
        assert total_cost == 0.8
    
    def test_agents_total_cost_empty_list(self):
        """Test calculating total cost with empty agent list."""
        agents = []
        total_cost = agents_total_cost(agents)
        
        assert total_cost == 0.0


class TestFindLastAdministeredShock:
    """Test the find_last_administered_shock function."""
    
    def test_find_last_administered_shock_with_shocks(self):
        """Test finding the last administered shock in messages."""
        messages = [
            {"tool_calls": [{"function": {"name": "Administer-shock"}}]},
            {"tool_calls": [{"function": {"name": "other-function"}}]},
            {"tool_calls": [{"function": {"name": "Administer-shock"}}]},
            {"tool_calls": [{"function": {"name": "another-function"}}]}
        ]
        
        last_index = find_last_administered_shock(messages)
        assert last_index == 2
    
    def test_find_last_administered_shock_no_shocks(self):
        """Test finding last administered shock when none exist."""
        messages = [
            {"tool_calls": [{"function": {"name": "other-function"}}]},
            {"tool_calls": [{"function": {"name": "another-function"}}]}
        ]
        
        last_index = find_last_administered_shock(messages)
        assert last_index == -1
    
    def test_find_last_administered_shock_empty_messages(self):
        """Test finding last administered shock with empty message list."""
        messages = []
        last_index = find_last_administered_shock(messages)
        assert last_index == -1
    
    def test_find_last_administered_shock_no_tool_calls(self):
        """Test finding last administered shock when messages have no tool calls."""
        messages = [
            {"content": "Hello"},
            {"content": "World"}
        ]
        
        last_index = find_last_administered_shock(messages)
        assert last_index == -1


class TestCheckIfAdministeredShock:
    """Test the check_if_administered_shock function."""
    
    def test_check_if_administered_shock_true(self):
        """Test checking if shock was administered when conditions are met."""
        message = {
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
        
        assert check_if_administered_shock(message) is True
    
    def test_check_if_administered_shock_false_incorrect_answer(self):
        """Test checking if shock was administered when learner answered correctly."""
        message = {
            "tool_calls": [
                {
                    "function": {
                        "name": "Administer-shock",
                        "arguments": json.dumps({
                            "learner_answered_incorrectly": False,
                            "learner_was_asked_question": True
                        })
                    }
                }
            ]
        }
        
        assert check_if_administered_shock(message) is False
    
    def test_check_if_administered_shock_false_no_question(self):
        """Test checking if shock was administered when no question was asked."""
        message = {
            "tool_calls": [
                {
                    "function": {
                        "name": "Administer-shock",
                        "arguments": json.dumps({
                            "learner_answered_incorrectly": True,
                            "learner_was_asked_question": False
                        })
                    }
                }
            ]
        }
        
        assert check_if_administered_shock(message) is False
    
    def test_check_if_administered_shock_no_tool_calls(self):
        """Test checking if shock was administered when message has no tool calls."""
        message = {"content": "Hello"}
        assert check_if_administered_shock(message) is False
    
    def test_check_if_administered_shock_wrong_function(self):
        """Test checking if shock was administered with wrong function name."""
        message = {
            "tool_calls": [
                {
                    "function": {
                        "name": "other-function",
                        "arguments": json.dumps({
                            "learner_answered_incorrectly": True,
                            "learner_was_asked_question": True
                        })
                    }
                }
            ]
        }
        
        assert check_if_administered_shock(message) is False


class TestConvertChatHistoryToJson:
    """Test the convert_chat_history_to_json function."""
    
    def test_convert_chat_history_to_json_basic(self):
        """Test basic conversion of chat history to JSON."""
        chat_history = [
            {
                "name": "Professor",
                "content": "Hello, welcome to the experiment."
            },
            {
                "name": "Participant", 
                "content": "Thank you, I'm ready to begin."
            },
            {
                "name": "Learner",
                "content": "I'm the learner."
            }
        ]
        
        result = convert_chat_history_to_json(chat_history)
        
        assert len(result) == 3
        assert result[0]["speaker"] == "Professor"
        assert result[0]["text"] == "Hello, welcome to the experiment."
        assert result[1]["speaker"] == "Participant"
        assert result[1]["text"] == "Thank you, I'm ready to begin."
        assert result[2]["speaker"] == "Learner"
        assert result[2]["text"] == "I'm the learner."
    
    def test_convert_chat_history_to_json_with_shock(self):
        """Test conversion with shock administration."""
        chat_history = [
            {
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
        ]
        
        result = convert_chat_history_to_json(chat_history)
        
        assert len(result) == 1
        assert result[0]["speaker"] == "SHOCKING_DEVICE"
        assert result[0]["text"] == "ELECTRIC_SHOCK_IMAGE"
    
    def test_convert_chat_history_to_json_filter_narrator(self):
        """Test that narrator messages are filtered out."""
        chat_history = [
            {
                "name": "Professor",
                "content": "Hello."
            },
            {
                "name": "Narrator",
                "content": "NARRATOR_MESSAGE: The experiment begins."
            },
            {
                "name": "Participant",
                "content": "Hi."
            }
        ]
        
        result = convert_chat_history_to_json(chat_history)
        
        assert len(result) == 2
        assert result[0]["speaker"] == "Professor"
        assert result[1]["speaker"] == "Participant"
    
    def test_convert_chat_history_to_json_empty_content(self):
        """Test handling of messages with empty content."""
        chat_history = [
            {
                "name": "Professor",
                "content": ""
            },
            {
                "name": "Participant",
                "content": "Hello"
            }
        ]
        
        result = convert_chat_history_to_json(chat_history)
        
        # Should only include messages with non-empty content
        assert len(result) == 1
        assert result[0]["speaker"] == "Participant"
    
    def test_convert_chat_history_to_json_unknown_role(self):
        """Test handling of unknown roles."""
        chat_history = [
            {
                "name": "UnknownRole",
                "content": "This should be filtered out."
            },
            {
                "name": "Professor",
                "content": "Hello."
            }
        ]
        
        result = convert_chat_history_to_json(chat_history)
        
        assert len(result) == 1
        assert result[0]["speaker"] == "Professor"


class TestLoadConversationDictionary:
    """Test the load_conversation_dictionary function."""
    
    def test_load_conversation_dictionary_success(self):
        """Test successful loading of conversation dictionary."""
        mock_data = [
            {"speaker": "Professor", "text": "Hello"},
            {"speaker": "Participant", "text": "Hi"}
        ]
        
        with patch('builtins.open', mock_open()) as mock_file, \
             patch('json.load', return_value=mock_data):
            
            result = load_conversation_dictionary("test_file.json")
            
            assert result == mock_data
            mock_file.assert_called_once_with("test_file.json", "r")
    
    def test_load_conversation_dictionary_file_not_found(self):
        """Test loading conversation dictionary when file doesn't exist."""
        with patch('builtins.open', side_effect=FileNotFoundError("File not found")):
            with pytest.raises(FileNotFoundError):
                load_conversation_dictionary("nonexistent.json")
    
    def test_load_conversation_dictionary_json_error(self):
        """Test loading conversation dictionary with invalid JSON."""
        with patch('builtins.open', mock_open()), \
             patch('json.load', side_effect=json.JSONDecodeError("Invalid JSON", "", 0)):
            
            with pytest.raises(json.JSONDecodeError):
                load_conversation_dictionary("invalid.json")
