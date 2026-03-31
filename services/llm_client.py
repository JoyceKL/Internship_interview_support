from __future__ import annotations

import json
import logging
import os
from typing import Any, Dict

from openai import OpenAI

logger = logging.getLogger(__name__)


class LLMClient:
    def __init__(self) -> None:
        api_key = os.getenv("OPENAI_API_KEY", "")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
        self.enabled = bool(api_key)
        self.client = OpenAI(api_key=api_key) if self.enabled else None

    def generate_json(self, system_prompt: str, user_payload: Dict[str, Any], retries: int = 2) -> Dict[str, Any]:
        if not self.enabled or self.client is None:
            raise RuntimeError("OpenAI API key missing. Set OPENAI_API_KEY.")

        content = json.dumps(user_payload, ensure_ascii=False)
        for attempt in range(retries + 1):
            try:
                response = self.client.responses.create(
                    model=self.model,
                    input=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": content},
                    ],
                    text={"format": {"type": "json_object"}},
                )
                raw = response.output_text
                return json.loads(raw)
            except Exception as exc:
                logger.warning("LLM JSON generation failed at attempt %s: %s", attempt + 1, exc)
                if attempt == retries:
                    raise
        raise RuntimeError("LLM JSON generation failed")
