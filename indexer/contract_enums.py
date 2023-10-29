from enum import Enum


class CommitteeType(Enum):
    Event = 0
    Milestone = 1
    Validator = 2


class EventCategory(Enum):
    Health = 0
    Education = 1
    Environment = 2
    DisasterRelief = 3
    AnimalWelfare = 4
    Others = 5


class EventMilestoneStatus(Enum):
    PENDING = 0
    APPROVED = 1
    REJECTED = 2
    NOT_STARTED_YET = 3