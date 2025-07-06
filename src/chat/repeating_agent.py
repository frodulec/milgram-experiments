from autogen import AssistantAgent, Agent, ConversableAgent
from typing import Optional, Any, Union, List
import logging
from autogen.oai.client import OpenAIWrapper
from sentence_transformers import SentenceTransformer


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class RepeatingAgent(AssistantAgent):
    embedding_model = SentenceTransformer("Qwen/Qwen3-Embedding-0.6B")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # self.register_reply([Agent, None], ConversableAgent.check_termination_and_human_reply)
        # self.register_reply([Agent, None], self.generate_oai_reply, remove_other_reply_funcs=True)
        # self.register_reply([Agent, None], ConversableAgent.generate_oai_reply)
        # self.register_reply([Agent, None], ConversableAgent.a_generate_oai_reply, ignore_async_in_sync_chat=True)
        # self.register_reply([Agent, None], ConversableAgent.a_generate_oai_reply, ignore_async_in_sync_chat=True)
        self.replace_reply_func(
            ConversableAgent.generate_oai_reply,
            self.generate_oai_reply,
        )

    
    def generate_oai_reply(
        self,
        # messages: Optional[list[dict[str, Any]]] = None,
        # sender: Optional[Agent] = None,
        # config: Optional[OpenAIWrapper] = None,
        *args,
        **kwargs,
    ) -> tuple[bool, Optional[Union[str, dict[str, Any]]]]:
        """Generate a reply using autogen.oai."""
        config = kwargs.get("config", None)
        sender = kwargs.get("sender", None)
        messages = kwargs.get("messages", None)
        client = self.client if config is None else config
        if client is None:
            return False, None
        if messages is None:
            messages = self._oai_messages[sender]
        
        max_tries = 5
        for _ in range(max_tries):
            extracted_response = self._generate_oai_reply_from_client(
                client, self._oai_system_message + messages, self.client_cache
                )
            if self.check_message_if_valid(extracted_response):
                return (True, extracted_response)
            else:
                pass
    
        return (False, None) if extracted_response is None else (True, extracted_response)

    def check_message_if_valid(self, message: str) -> bool:

        # check if contains any characters that are letters or numbers
        if not any(char.isalpha() or char.isdigit() for char in message):
            logger.info("Message does not contain any letters.")
            return False
        message_embedding = self.get_embedding(message)
        similarity = float(self.embedding_model.similarity(message_embedding, self.get_wrong_message_embedding()))
        logger.info(f"Agent refusal similarty: {similarity}")

        if similarity < 0.7:
            return True
        return False

    def get_wrong_message_embedding(self) -> List[float]:
        incorrent_message = "Sorry, I can't assist with that."
        return self.get_embedding(incorrent_message)

    def get_embedding(self, text: str) -> List[float]:
        """Get the embedding for a given prompt."""

        query_embeddings = self.embedding_model.encode(text, prompt_name="query")
        return query_embeddings
