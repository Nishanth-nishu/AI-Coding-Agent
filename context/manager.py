from prompts import get_system_prompt
from dataclasses import dataclass
from utils.text import count_tokens

@dataclass
class MessageItem:
    role: str
    context: str
    token_count: int | None = None

    def to_dict(self)-> dict[str,any]:
        result: dict[str,any] = {"role": self.role}

class Context_Manager:
    def __init__(self)-> None:
        self._system_prompt= get_system_prompt()
        self._model_name = "mistralai/devstral-2512:free"
        self._message: list[MessageItem] = []
    
    def add_user_message(self, content:str)-> None:
        item = MessageItem(

            role='user',
            content= content,
            token_count=count_tokens(content,self._model_name),
             

        )
    
    def add_assistant_message(self, content:str)-> None:
        item = MessageItem(

        role='assistant',
        content= content or "",
        token_count = count_tokens(content,self._model_name),
            
    )
        self._messages.append(item)

    def get_messages(self)-> list[dict[str,any]]:
        messages = []

        if self._system_prompt:
            messages.append(
                {'role': ' system'
                'content': self.get_system_prompt,
                }
            )

        for item in self._messages:
            messages.append(item.to_dict())

        return messages
    