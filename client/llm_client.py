import asyncio
from collections.abc import AsyncGenerator
from openai import APIConnectionError, APIError, AsyncOpenAI, RateLimitError

from response import StreamEventType, StreamEvent, TextDelta , TokkenUsage

class LLMClient:
    def __init__(self)  -> None:
        self._client : AsyncOpenAI | None= None
        self._max_retries : int = 3

    def get_client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key="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",
                base_url="https://openrouter.ai/api/v1", 
            )

        return self._client 

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def chat_completion(self, message: list[dict[str, any]], stream: bool=True)-> AsyncGenerator[StreamEvent, None]:
        
        client = self.get_client()
        kwargs = {
                    "model": "mistralai/devstral-2512:free",
                    "messages": message,
                    "stream": stream,
                }
        for attempt in range(self._max_retries+1):
            try:
                if stream:
                    async for event in self._stream_response(client, kwargs):
                        yield event
                else:
                    event = await self._non_stream_response(client, kwargs)
                    yield event
                return
            except RateLimitError as e:
                if attempt < self._max_retries:
                    wait_time = 2 ** attempt
                    await asyncio.sleep(wait_time)
                else:
                    yield StreamEvent(
                        type=StreamEventType.ERROR,
                        error=f"The rate limit has been exceeded. {str(e)}"
                    )
                    return
            
            except APIConnectionError as e:
                if attempt < self._max_retries:
                    wait_time = 2** attempt
                    await asyncio.sleep(wait_time)
                else:
                    yield StreamEvent(
                        type=StreamEventType.ERROR,
                        error=f"API connection error occurred: {str(e)}"
                    )
            except APIError as e:
                yield StreamEvent(
                    type=StreamEventType.ERROR,
                    error=f"API error occurred: {str(e)}"
                )
                return

    async def _stream_response(self,client: AsyncOpenAI, kwargs: dict[str, any]) -> AsyncGenerator[StreamEvent, None]:
        response = await client.chat.completions.create(**kwargs)

        usage: TokkenUsage | None = None
        finish_reason: str | None = None
        async for chunk in response:
            if hasattr(chunk, "usage") and chunk.usage:
                usage = TokkenUsage(
                    prompt_tokens=chunk.usage.prompt_tokens,
                    completion_tokens=chunk.usage.completion_tokens,
                    total_tokens=chunk.usage.total_tokens,
                    cashed_tokens=chunk.usage.prompt_tokens_details.cached_tokens,
                )
            if not chunk.choices:
                continue

            choice = chunk.choices[0]
            delta = choice.delta

            if choice.finish_reason:
                finish_reason = choice.finish_reason
            
            if delta.content:
                yield StreamEvent(
                    type=StreamEventType.TEXT_DELTA,
                    text_delta=TextDelta(content=delta.content)
                )

        yield StreamEvent(
            type=StreamEventType.MESSAGE_COMPLETE,
            finish_reason=finish_reason,
            usage=usage
        )

    async def _non_stream_response(self, client: AsyncOpenAI, kwargs: dict[str, any]) -> StreamEvent:
        response = await client.chat.completions.create(**kwargs)
        choice = response.choices[0]
        message = choice.message
        text_delta= None
        if message.content:
            text_delta = TextDelta(content=message.content)
        usage = None
        if response.usage:
            usage = TokkenUsage(
                prompt_tokens=response.usage.prompt_tokens,
                completion_tokens=response.usage.completion_tokens,
                total_tokens=response.usage.total_tokens,
                cashed_tokens=response.usage.prompt_tokens_details.cached_tokens,
            ) 
        return StreamEvent(
            type=StreamEventType.MESSAGE_COMPLETE,
            text_delta=text_delta,
            finish_reason=choice.finish_reason,
            usage=usage)