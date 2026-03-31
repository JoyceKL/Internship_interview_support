from __future__ import annotations

import json
import logging
from typing import Any, TypeVar

from openai import OpenAI
from pydantic import BaseModel, ValidationError

from backend.core.config import settings

logger = logging.getLogger(__name__)
T = TypeVar("T", bound=BaseModel)


class OpenAIAdapter:
    def __init__(self) -> None:
        self.enabled = bool(settings.openai_api_key)
        self.client = OpenAI(api_key=settings.openai_api_key) if self.enabled else None

    def structured_json(self, *, system_prompt: str, user_payload: dict[str, Any], schema_model: type[T]) -> T:
        if not self.enabled or self.client is None:
            raise RuntimeError("OpenAI is not configured")
        schema = schema_model.model_json_schema()
        last_error: Exception | None = None
        for _ in range(settings.openai_max_retries + 1):
            try:
                response = self.client.responses.create(
                    model=settings.openai_model,
                    input=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
                    ],
                    text={"format": {"type": "json_schema", "name": schema_model.__name__, "schema": schema, "strict": True}},
                )
                payload = json.loads(response.output_text)
                return schema_model.model_validate(payload)
            except (ValidationError, Exception) as exc:
                last_error = exc
                logger.warning("Structured output attempt failed: %s", exc)
        raise RuntimeError(f"Structured output failed after retries: {last_error}")
