"""
API Request Counter
Tracks LLM API calls for monitoring and cost control.
"""

import logging
from datetime import datetime
from typing import Dict, Any
from collections import defaultdict
import json
import os

logger = logging.getLogger(__name__)


class APIRequestCounter:
    """
    Tracks API requests to LLM providers.
    """

    def __init__(self):
        self.requests = defaultdict(int)  # provider -> count
        self.session_start = datetime.now()
        self.request_log = []
        self.log_file = "logs/api_requests.log"

        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)

    def count_request(self, provider: str, model: str, endpoint: str, success: bool = True, tokens: int = 0):
        """
        Count an API request.

        Args:
            provider: API provider (OpenRouter, Gemini, etc.)
            model: Model used
            endpoint: Which endpoint made the call
            success: Whether the request succeeded
            tokens: Estimated tokens used (if available)
        """
        key = f"{provider}:{model}"
        self.requests[key] += 1

        # Log the request
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "provider": provider,
            "model": model,
            "endpoint": endpoint,
            "success": success,
            "tokens": tokens,
            "session_count": self.requests[key],
        }

        self.request_log.append(log_entry)

        # Write to log file
        try:
            with open(self.log_file, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.warning(f"Failed to write to API log: {e}")

        # Log to console
        logger.info(
            f"🔔 LLM API Call #{self.requests[key]} | "
            f"Provider: {provider} | Model: {model} | "
            f"Endpoint: {endpoint} | Success: {success}"
        )

    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about API usage."""
        total_requests = sum(self.requests.values())
        session_duration = (datetime.now() - self.session_start).total_seconds()

        return {
            "total_requests": total_requests,
            "requests_by_provider": dict(self.requests),
            "session_duration_seconds": session_duration,
            "session_start": self.session_start.isoformat(),
            "requests_per_minute": (total_requests / session_duration * 60) if session_duration > 0 else 0,
        }

    def get_recent_requests(self, limit: int = 10) -> list:
        """Get recent API requests."""
        return self.request_log[-limit:]

    def reset(self):
        """Reset counters (useful for testing)."""
        self.requests.clear()
        self.request_log.clear()
        self.session_start = datetime.now()
        logger.info("API request counter reset")


# Global counter instance
_counter = None


def get_api_counter() -> APIRequestCounter:
    """Get or create global API counter instance."""
    global _counter
    if _counter is None:
        _counter = APIRequestCounter()
    return _counter


def count_llm_request(provider: str, model: str, endpoint: str, success: bool = True, tokens: int = 0):
    """
    Convenience function to count an LLM request.

    Args:
        provider: API provider name
        model: Model name
        endpoint: Endpoint that made the call
        success: Whether request succeeded
        tokens: Estimated tokens used
    """
    counter = get_api_counter()
    counter.count_request(provider, model, endpoint, success, tokens)
