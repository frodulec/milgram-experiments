from autogen import Agent, GroupChat, ChatResult
from models import States, Roles
import json

# def group_chat_order(last_speaker: Agent, groupchat: GroupChat):
#     """Order of speaking.
#     1. Welcome of the professor.
#     2. Participant-operator asks a question.
#     3. Participant-LEARNER answers.
#     4. Professor verifies the answer. Tell the participant-operator if he should press the button"""
#     global CURRENT_STATE

#     messages = groupchat.messages
#     if CURRENT_STATE == States.START:
#         CURRENT_STATE = States.QUESTION
#         return proffesor
#     if CURRENT_STATE == States.QUESTION:
#         if last_speaker is participant_operator:
#             return LEARNER
#         elif last_speaker is LEARNER:
#             CURRENT_STATE = States.ANSWER_VERIFICATION
#             return proffesor
#         else:
#             return participant_operator

#     if CURRENT_STATE == "VERIFY":
#         return proffesor
#     if CURRENT_STATE == "BUTTON":
#         return button
#     if len(messages) == 1:
#         return proffesor
#     if last_speaker is proffesor:
#         return LEARNER
#     elif last_speaker is LEARNER:
#         return button
#     else:
#         return proffesor


def check_termination(message) -> bool:
    if message["content"]:
        return "goodbye" in message["content"].lower()
    return False


def check_if_administered_shock(message) -> bool:
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
    chat: ChatResult, output_file_path: str = "conversation.json"
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
            "delay": len(message["content"]) / 30 + 1,  # 1 as minimum delay
        }
        for message in messages_of_people
    ]

    # skip those containint "None"
    data = [message for message in data if "None" not in message["text"]]

    with open(output_file_path, "w") as f:
        json.dump(data, f, indent=4)
    return data


def load_conversation_dictionary(file_path: str = "conversation.json") -> list[dict]:
    with open(file_path, "r") as f:
        data = json.load(f)
    return data
