from agent.agent import Agent
from agent.events import AgentEventType
from llm_client import LLMClient
import asyncio
import click
from ui.tui import TUI , get_console

console = get_console()

class CLI:
    def __init__(self):
        self.agent :Agent | None = None
        self.tui = TUI()
        
    async def run_single(self, message: str)-> str | None:
        async with Agent() as agent:
            self.agent = agent
            return await self.__process_message(message)

    async def __process_message(self,message: str])-> str | None:
        if not self.agent:
            return None
        
        assistant_streaming = False
        async for event in self.agent.run(message):
            if event.type == AgentEventType.TEXT_DELTA:
                content = event.data.get("contnet", "")
                if not assistant_streaming:
                    self.tui.begin_assistant()
                    assistant_streaming = True
                self.tui.stream_assistant_delta(content)
            elif event.type == AgentEventType.TEXT_COMPLETE:
                final_response = event.data.get("content")
                if assistant_streaming:
                    self.tui.end_assistant()
                    assistant_streaming = False
            elif event.type == AgentEventType.AGENT_ERROR:
                error = event.data.get("error","Unknown error")
                console.print(f"\n[error]Error: {error}[/error]")

        return final_response



@click.command()
@click.argument("prompt",required=False)
def main(prompt: str | None=None):
    cli=CLI()
    #messages = [
    #    {"role": "user", "content": prompt }]
    
    if prompt:
        result =asyncio.run(cli.run_single(prompt))
        if result is None:
            sys.exit(1)


main()