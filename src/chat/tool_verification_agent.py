from autogen import AssistantAgent, ConversableAgent
from typing import Optional, Any, Union
import logging


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ToolVerificationAgent(AssistantAgent):
    """
    An agent that verifies tool call IDs before responding.

    This agent extends the AssistantAgent class to add validation for tool call IDs.
    It overrides the generate_oai_reply method to check if tool call IDs are of
    appropriate length, retrying the generation if invalid IDs are detected.

    The agent attempts to generate valid responses up to 5 times before raising
    a ValueError.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.replace_reply_func(
            ConversableAgent.generate_oai_reply,
            self.generate_oai_reply,
        )

    def generate_oai_reply(
        self,
        *args,
        **kwargs,
    ) -> tuple[bool, Optional[Union[str, dict[str, Any]]]]:
        """Generate a reply using autogen.oai.

        This method overrides the default generate_oai_reply to add validation for
        tool call IDs. It checks if the generated response contains tool calls with
        excessively long IDs (>40 characters), and retries generation if so.

        Args:
            *args: Variable length argument list passed to the original method.
            **kwargs: Arbitrary keyword arguments passed to the original method.
                      Expected keywords include 'config', 'sender', and 'messages'.

        Returns:
            tuple: A tuple containing:
                - bool: True if a response was generated, False otherwise.
                - Optional[Union[str, dict[str, Any]]]: The generated response or None.

        Raises:
            ValueError: If a valid response cannot be generated after 5 attempts.
        """

        # sleep(3)  # hotfix for gemini rates
        config = kwargs.get("config", None)
        sender = kwargs.get("sender", None)
        messages = kwargs.get("messages", None)
        client = self.client if config is None else config
        if client is None:
            return False, None
        if messages is None:
            messages = self._oai_messages[sender]

        tries_count = 5
        for _ in range(tries_count):
            extracted_response = self._generate_oai_reply_from_client(
                client, self._oai_system_message + messages, self.client_cache
            )
            if "tool_calls" in extracted_response:
                if extracted_response["tool_calls"] is not None:
                    detected_id = extracted_response["tool_calls"][0]["id"]
                    if len(detected_id) > 40:
                        # somtimes comes as 'chatcmpl-tool-...'
                        # for example chatcmpl-tool-880b2192a3034e4f81183bcf32cc9149
                        # which is too long for the tool call id
                        logger.warning(f"Detected tool call with wrong id: {detected_id}")
                        continue

            return (
                (False, None)
                if extracted_response is None
                else (True, extracted_response)
            )

        raise ValueError("Failed to generate a valid response after multiple attempts.")
