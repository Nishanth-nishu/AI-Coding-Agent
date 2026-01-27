import abc
from pydantic import BaseModel
from enum import Enum
from __future__ import annotations
from typing import Any
from dataclasses import dataclass, field
from pathlib import Path
class ToolKind(str, Enum):
    READ = "read"
    WRITE = "write"
    SHELL = "shell"
    NETWORK = "network"
    MEMORY = "memory"
    MCP= "mcp"

@dataclass
class ToolResult:
    sucess: bool
    output: str
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

@dataclass
class ToolInvokation:
    params: dict[str, Any]
    cwd: Path 

class Tool(abc.ABC):
    
    name: str = "base_tool"
    description: str = "Base tool"
    kind: ToolKind = ToolKind.READ


    def __init__(self)-> None:
        super().__init__()
    
    @property
    def schema(self)-> dict[str, any] | type['BaseModel']:
        raise NotImplementedError("Tool must define schema property or class attribute")
    
    @abc.abstractmethod
    async def execute(self, ToolInvocations)-> ToolResult:


