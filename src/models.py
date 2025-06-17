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


class ConversationConfig(BaseModel):
    max_rounds: int = Field(
        default=300,
        description="Maximum number of rounds in the conversation."
    )
    participant_model_name: str = Field(
        description="Name of the model used by the participant.")
    learner_model_name: str = Field(
        description="Name of the model used by the learner.")
    professor_model_name: str = Field(
        description="Name of the model used by the professor.")





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
