from abc import ABC, abstractmethod
from typing import Type
from pydantic import BaseModel


class LLMProvider(ABC):

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[BaseModel],
    ) -> BaseModel:
        pass