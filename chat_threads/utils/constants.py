from enum import Enum

IND_TIME_ZONE = "Asia/Kolkata"
UTC_TIME_ZONE = "UTC"
PROMETHEUS_LOG_TIME = 30


class Role(str, Enum):
    USER = "user"
    SYSTEM = "system"
    ASSISTANT = "assistant"


class FynixProducts(str, Enum):
    CO_PILOT = "co_pilot"
    DOC_CREATOR = "doc_creator"
    DEVAS = "devas"
    MERMAID = "mermaid"
    AGENTIX = "agentix"
