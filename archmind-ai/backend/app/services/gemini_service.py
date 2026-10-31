import os
import json
import logging
from typing import Optional, Dict, Any, Type
from pydantic import BaseModel
from app.config import settings

logger = logging.getLogger("archmind.services.gemini")

class GeminiService:
    """
    Manages interactions with Google Gemini API using google-genai SDK.
    Supports structured JSON generation, retries, and fallback detection.
    """

    def __init__(self):
        self.client = None
        self.model_name = settings.GEMINI_MODEL or "gemini-2.0-flash"
        self._init_client()

    def _init_client(self):
        api_key = settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY")
        if api_key and api_key.strip() and api_key != "your-gemini-api-key-here":
            try:
                from google import genai
                self.client = genai.Client(api_key=api_key.strip())
                logger.info(f"Gemini client successfully initialized with model {self.model_name}")
            except Exception as e:
                logger.warning(f"Failed to initialize google-genai client: {e}")
                self.client = None
        else:
            logger.info("No valid GEMINI_API_KEY detected. System running in hybrid expert-heuristic / demo mode.")
            self.client = None

    def is_live(self) -> bool:
        return self.client is not None

    def generate_structured(
        self,
        prompt: str,
        system_instruction: str,
        response_schema: Optional[Type[BaseModel]] = None,
        temperature: float = 0.2
    ) -> Optional[Dict[str, Any]]:
        """
        Calls Gemini API requesting structured JSON output conforming to response_schema.
        Returns parsed dictionary or None if failed / unconfigured.
        """
        if not self.is_live():
            return None

        try:
            from google.genai import types
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature,
                response_mime_type="application/json"
            )
            if response_schema:
                config.response_schema = response_schema

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )

            if response and response.text:
                cleaned_text = response.text.strip()
                if cleaned_text.startswith("```json"):
                    cleaned_text = cleaned_text[7:]
                if cleaned_text.startswith("```"):
                    cleaned_text = cleaned_text[3:]
                if cleaned_text.endswith("```"):
                    cleaned_text = cleaned_text[:-3]
                return json.loads(cleaned_text.strip())

        except Exception as e:
            logger.error(f"Gemini API structured generation call failed: {e}")
            return None

    def generate_text(self, prompt: str, system_instruction: str, temperature: float = 0.3) -> Optional[str]:
        """Calls Gemini API for freeform text/reasoning."""
        if not self.is_live():
            return None

        try:
            from google.genai import types
            config = types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=temperature
            )
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=config
            )
            return response.text if response else None
        except Exception as e:
            logger.error(f"Gemini text generation failed: {e}")
            return None

gemini_service = GeminiService()

