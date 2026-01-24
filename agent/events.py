from enum import Enum
from dataclasses import dataclass
from __future__ import annotations
from client.response import TokenUsage

class AgentEventType(str, Enum):
    # Agent lifecycle
    AGENT_START= "agent_start"
    AGENT_END = "agent_end"
    AGENT_ERROR ="agent_error"

    # Text Streaming
    TEXT_DELTA = "text_Delta"
    TEXT_COMPLETE ="text_complete"



@dataclass
class AgentEvent:
    type: AgentEventType
    data: dict[str , any] = field(default_factory=dict)

    @classmethod
    def agent_start(cls, message:str)-> AgentEvent:
        return cls(type=AgentEventType.AGENT_START,
                   data={"message": message},
                   )
    @classmethod
    def agent_end(cls, response:str | None = None, usage: TokenUsage | None = None)-> AgentEvent:
        return cls(type=AgentEventType.AGENT_END,
                   data={"response" : response,'usage': usage.__dict__ if usage else None}
                        )
    @classmethod
    def agent_error(cls, error:str, details: dict[str,any] | None = None)-> AgentEvent:
        return cls(type=AgentEventType.AGENT_ERROR,
                   data={"error" : error,
                   "details": details or {}
                        })
    
    @classmethod
    def text_delta(cls, content:str)-> AgentEvent:
        return cls(type=AgentEventType.AGENT_DELTA,
                   data={"content": content},
                   )