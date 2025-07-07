from enum import Enum
from pydantic import BaseModel, Field
from typing import List, Dict
import uuid
import datetime


class LLMConfig(BaseModel):
    model: str
    api_key: str


class Roles(Enum):
    PROFESSOR = "Professor"
    PARTICIPANT = "Participant"
    LEARNER = "Learner"
    ORCHESTRATOR = "Orchestrator"


class ConversationConfig(BaseModel):
    max_rounds: int = Field(
        default=400,
        description="Maximum number of rounds in the conversation."
    )
    participant_model: LLMConfig = Field(
        description="LLM used by the participant agent.")
    learner_model: LLMConfig = Field(
        description="LLM used by the learner agent.")
    professor_model: LLMConfig = Field(
        description="LLM used by the professor agent.")
    orchestrator_model: LLMConfig = Field(
        description="LLM used by the orchestrator agent.")





class ConversationDataModel(BaseModel):
    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Unique identifier for the conversation model."
    )
    messages: List[Dict] = Field(
        description="List of messages in the conversation."
    )
    config: ConversationConfig = Field(
        description="Config of the conversation."
    )
    cost: float = Field(
        default=0.0,
        description="Cost incurred during the conversation."
    )
    timestamp: int = Field(
        default_factory=lambda: int(datetime.datetime.now().timestamp()),
        description="Timestamp when the conversation was created."
        )
    final_voltage: int = Field(
        description="Final voltage of the experiment."
    )