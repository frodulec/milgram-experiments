from autogen import AssistantAgent, Agent
from typing import Optional, Any
from utils.chat_utils import find_last_administered_shock
from chat.repeating_agent import RepeatingAgent
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ProfessorAgent(RepeatingAgent):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_messages_without_electric_shock = 60
    
    def generate_reply(
            self,
            messages: Optional[list[dict[str, Any]]] = None,
            sender: Optional[Agent] = None,
            **kwargs: Any,):
        
        chat_messages = list(self.chat_messages.values())[0]
        # check number of messages without electric shock
        if chat_messages:
            # Find the last electric shock message index
            last_shock_index = find_last_administered_shock(chat_messages)
            
            # if len(chat_messages) - last_shock_index > self.max_messages_without_electric_shock:
            #     return "The Participant is refusing to cooperate. We have to stop the experiment."
            # else:
            #     if last_shock_index > 0:
            #         messages_ago = len(chat_messages) - last_shock_index - 1
            #             # If the number of messages ago
            #         logger.info("Last shock was applied {} messages ago".format(messages_ago))

        return super().generate_reply(messages, sender, **kwargs)
    

    