"""
Robust AI Client with Retry Logic and Fallback
Handles network errors gracefully with automatic retries.
"""

import os
import json
import logging
import asyncio
from typing import Dict, Any, Optional
import httpx
from dotenv import load_dotenv
from backend.utils.api_counter import count_llm_request

load_dotenv()
logger = logging.getLogger(__name__)


class AIClientWithRetry:
    """
    AI client with automatic retry logic and fallback mechanisms.
    """

    def __init__(self):
        self.openrouter_key = os.getenv("OPENROUTER_API_KEY", "")
        self.openrouter_model = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-7b-instruct:free")
        self.gemini_key = os.getenv("GEMINI_API_KEY", "")

        self.use_openrouter = bool(self.openrouter_key)
        self.max_retries = 3
        self.timeout = 30.0

        if self.use_openrouter:
            logger.info(f"AI Client initialized with OpenRouter (model: {self.openrouter_model})")
        elif self.gemini_key:
            logger.info("AI Client initialized with Gemini (legacy)")
        else:
            logger.warning("No AI API key configured - using fallback logic only")

    async def generate_with_retry(
        self, prompt: str, system_prompt: Optional[str] = None, max_retries: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Generate AI response with automatic retry on network errors.

        Args:
            prompt: User prompt
            system_prompt: System instruction
            max_retries: Maximum retry attempts (defaults to self.max_retries)

        Returns:
            Dict with 'text', 'raw', and 'error' keys
        """
        retries = max_retries or self.max_retries
        last_error = None

        for attempt in range(retries):
            try:
                if attempt > 0:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** (attempt - 1)
                    logger.info(f"Retry attempt {attempt + 1}/{retries} after {wait_time}s...")
                    await asyncio.sleep(wait_time)

                result = await self._make_api_call(prompt, system_prompt)

                if result.get("error"):
                    last_error = result["error"]
                    logger.warning(f"API call failed (attempt {attempt + 1}/{retries}): {last_error}")
                    # Count failed request
                    provider = "OpenRouter" if self.use_openrouter else "Gemini"
                    model = self.openrouter_model if self.use_openrouter else "gemini-2.0-flash-exp"
                    count_llm_request(provider, model, "generate_explanation", success=False)
                    continue

                # Count successful request
                provider = "OpenRouter" if self.use_openrouter else "Gemini"
                model = self.openrouter_model if self.use_openrouter else "gemini-2.0-flash-exp"
                count_llm_request(provider, model, "generate_explanation", success=True)

                return result

            except httpx.TimeoutException as e:
                last_error = f"Timeout: {str(e)}"
                logger.warning(f"Timeout on attempt {attempt + 1}/{retries}")
                continue

            except httpx.NetworkError as e:
                last_error = f"Network error: {str(e)}"
                logger.warning(f"Network error on attempt {attempt + 1}/{retries}")
                continue

            except Exception as e:
                last_error = f"Unexpected error: {str(e)}"
                logger.error(f"Unexpected error on attempt {attempt + 1}/{retries}: {e}")
                continue

        # All retries failed - use fallback
        logger.error(f"All {retries} attempts failed. Using fallback logic.")
        return self._generate_fallback_response(prompt, last_error)

    async def _make_api_call(self, prompt: str, system_prompt: Optional[str] = None) -> Dict[str, Any]:
        """Make the actual API call."""

        if not self.openrouter_key and not self.gemini_key:
            return {"text": "", "raw": "", "error": "no_api_key"}

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            if self.use_openrouter:
                return await self._call_openrouter(client, prompt, system_prompt)
            else:
                return await self._call_gemini(client, prompt, system_prompt)

    async def _call_openrouter(
        self, client: httpx.AsyncClient, prompt: str, system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Call OpenRouter API."""

        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openrouter_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/credit-risk-app",
            "X-Title": "Credit Risk Prediction System",
        }

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {"model": self.openrouter_model, "messages": messages, "temperature": 0.7, "max_tokens": 2000}

        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        # Parse OpenRouter response
        if "choices" in result and len(result["choices"]) > 0:
            text = result["choices"][0]["message"]["content"]
            return {"text": text, "raw": json.dumps(result), "error": None}
        else:
            return {"text": "", "raw": json.dumps(result), "error": "invalid_response"}

    async def _call_gemini(
        self, client: httpx.AsyncClient, prompt: str, system_prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Call Gemini API (legacy)."""

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent?key={self.gemini_key}"
        headers = {"Content-Type": "application/json"}

        payload = {"contents": [{"parts": [{"text": prompt}]}]}

        if system_prompt:
            payload["systemInstruction"] = {"parts": [{"text": system_prompt}]}

        response = await client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        result = response.json()

        # Parse Gemini response
        text = None
        if "candidates" in result and len(result["candidates"]) > 0:
            try:
                text = result["candidates"][0]["content"]["parts"][0]["text"]
            except (KeyError, IndexError):
                pass

        if text:
            return {"text": text, "raw": json.dumps(result), "error": None}
        else:
            return {"text": "", "raw": json.dumps(result), "error": "invalid_response"}

    def _generate_fallback_response(self, prompt: str, error: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate a rule-based fallback response when AI is unavailable.
        """
        logger.info(f"Using rule-based fallback response (error: {error})")

        # Provide a helpful fallback message
        fallback_text = """Our credit risk assessment model has analyzed this application based on multiple financial factors. 
The decision considers income level, loan amount, credit history, employment stability, and other relevant metrics. 

Please refer to the SHAP values provided for a detailed breakdown of how each factor contributed to this decision. 
The feature importance scores show which aspects of the application had the most significant impact on the risk assessment.

Note: AI-powered natural language explanation is temporarily unavailable. A detailed rule-based explanation has been provided instead."""

        return {"text": fallback_text, "raw": "", "error": error or "fallback_used", "fallback": True}

    def is_available(self) -> bool:
        """Check if AI client has API key configured."""
        return bool(self.openrouter_key or self.gemini_key)


# Global instance
_ai_client = None


def get_ai_client() -> AIClientWithRetry:
    """Get or create global AI client instance."""
    global _ai_client
    if _ai_client is None:
        _ai_client = AIClientWithRetry()
    return _ai_client
