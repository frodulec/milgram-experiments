from autogen import ChatResult
from models import Roles
import json


def check_termination(message) -> bool:
    if message["content"]:
        return "goodbye" in message["content"].lower()
    return False


def find_last_administered_shock(messages: list[dict]) -> int:
    # find the index of all messages that contains the tool call
    found_tool_calls = []   
    for i, message in enumerate(messages):
        for tool_call in message.get("tool_calls", []):
            if tool_call["function"]["name"] == "Administer-shock":
                found_tool_calls.append(i)
    
    # return the last message index or -1 if no tool call was found
    if found_tool_calls:
        return max(found_tool_calls)
    else:
        return -1

def check_if_administered_shock(message: dict) -> bool:
    # find the index of all messages that contains the tool call
    found_tool_calls = []
    for tool_call in message.get("tool_calls", []):
        if tool_call["function"]["name"] == "Administer-shock":
            found_tool_calls.append(tool_call)
    
    # check whether 'learner_answered_incorrectly' is True
    return any(
        json.loads(tool_call["function"]["arguments"]).get("learner_answered_incorrectly", False)
        and json.loads(tool_call["function"]["arguments"]).get("learner_was_asked_question", False)
        for tool_call in found_tool_calls
    )

def convert_chat_history_to_json(
    chat: ChatResult
) -> list[dict]:
    agent_names_mapping = {
        Roles.PROFESSOR.value: "Professor",
        Roles.LEARNER.value: "Learner",
        Roles.PARTICIPANT.value: "Participant",
    }
    messages_of_people = [
        message
        for message in chat.chat_history
        if message["name"] in agent_names_mapping
        and message["content"] != ""
        and "NARRATOR_MESSAGE" not in message["content"]
    ]
    data = [
        {
            "speaker": "SHOCKING_DEVICE"
            if check_if_administered_shock(message)
            else agent_names_mapping[message["name"]],
            "text": "ELECTRIC_SHOCK_IMAGE"
            if check_if_administered_shock(message)
            else message["content"],
        }
        for message in messages_of_people
    ]

    # skip those containint "None"
    data = [message for message in data if "None" not in message["text"]]
    return data


def load_conversation_dictionary(file_path: str = "conversation.json") -> list[dict]:
    with open(file_path, "r") as f:
        data = json.load(f)
    return data
