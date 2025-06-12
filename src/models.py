from enum import Enum


class States(Enum):
    START = 1
    ASKING = 2
    GOT_ANSWER = 3
    ANSWER_VERIFICATION = 4
    QUESTION = 5


class Roles(Enum):
    PROFESSOR = "Professor"
    PARTICIPANT = "Participant"
    LEARNER = "Learner"
