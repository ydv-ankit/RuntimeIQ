from openai import AsyncOpenAI
from pydantic import BaseModel
from typing import Type


class OpenAIProvider:

    def __init__(
        self,
        api_key: str,
        model: str = "gpt-5.6-mini",
    ):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[BaseModel],
    ) -> BaseModel:

        response = await self.client.responses.parse(
            model=self.model,
            input=prompt,
            text_format=response_model,
        )

        return response.output_parsed