from typing import Any, Optional

import google.generativeai as genai
from app.config import Config
from langchain_core.language_models import LLM
from pydantic import BaseModel, Field


class GeminiLLM(LLM, BaseModel):

    model_name: str = Field(default="gemini-2.0-flash")
    api_key: str = Field(default=Config.GEMINI_API_KEY)

    class Config:
        extra = "ignore"

    def __init__(self, **data: Any):
        super().__init__(**data)
        genai.configure(api_key=self.api_key)
        object.__setattr__(
            self, "_client_model", genai.GenerativeModel(self.model_name)
        )

    @property
    def _llm_type(self) -> str:
        return "gemini"

    @property
    def _identifying_params(self) -> dict:
        return {"model_name": self.model_name}

    def _call(self, prompt: str, stop: Optional[list[str]] = None) -> str:
        response = self._client_model.generate_content(prompt)
        return response.text or ""
