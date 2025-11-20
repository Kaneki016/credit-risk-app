"""
API Configuration for Gemini API Keys
Manages separate API keys for different features to control usage.
"""

import logging
import os

from dotenv import load_dotenv

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class GeminiConfig:
    """Configuration for Gemini API usage."""

    def __init__(self):
        # API Keys - Separate keys for different features
        self.predictions_key = os.getenv("GEMINI_API_KEY_PREDICTIONS") or os.getenv("GEMINI_API_KEY", "")
        self.chatbot_key = os.getenv("GEMINI_API_KEY_CHATBOT") or os.getenv("GEMINI_API_KEY", "")

        # Feature toggles
        self.enable_shap_explanations = os.getenv("ENABLE_SHAP_EXPLANATIONS", "true").lower() == "true"
        self.enable_chatbot = os.getenv("ENABLE_CHATBOT", "true").lower() == "true"

        # API URL
        self.api_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"

        # Log configuration
        self._log_config()

    def _log_config(self):
        """Log the current configuration."""
        logger.info("=" * 70)
        logger.info("Gemini API Configuration")
        logger.info("=" * 70)
        logger.info(f"SHAP Explanations: {'✅ Enabled' if self.enable_shap_explanations else '❌ Disabled'}")
        logger.info(f"Chatbot: {'✅ Enabled' if self.enable_chatbot else '❌ Disabled'}")

        if self.predictions_key:
            logger.info(f"Predictions API Key: Configured ({self.predictions_key[:10]}...)")
        else:
            logger.warning("Predictions API Key: Not configured")

        if self.chatbot_key:
            logger.info(f"Chatbot API Key: Configured ({self.chatbot_key[:10]}...)")
        else:
            logger.warning("Chatbot API Key: Not configured")

        # Check if using same key
        if self.predictions_key and self.chatbot_key:
            if self.predictions_key == self.chatbot_key:
                logger.info("ℹ️  Using same API key for both features")
            else:
                logger.info("✅ Using separate API keys for each feature")

        logger.info("=" * 70)

    def get_predictions_key(self) -> str:
        """Get the API key for predictions/SHAP explanations."""
        return self.predictions_key

    def get_chatbot_key(self) -> str:
        """Get the API key for chatbot."""
        return self.chatbot_key

    def is_shap_enabled(self) -> bool:
        """Check if SHAP explanations are enabled."""
        return self.enable_shap_explanations and bool(self.predictions_key)

    def is_chatbot_enabled(self) -> bool:
        """Check if chatbot is enabled."""
        return self.enable_chatbot and bool(self.chatbot_key)

    def get_usage_stats(self) -> dict:
        """Get configuration stats for monitoring."""
        return {
            "shap_explanations": {
                "enabled": self.enable_shap_explanations,
                "has_key": bool(self.predictions_key),
                "operational": self.is_shap_enabled(),
            },
            "chatbot": {
                "enabled": self.enable_chatbot,
                "has_key": bool(self.chatbot_key),
                "operational": self.is_chatbot_enabled(),
            },
            "using_separate_keys": (
                self.predictions_key != self.chatbot_key if (self.predictions_key and self.chatbot_key) else False
            ),
        }


# Global configuration instance
gemini_config = GeminiConfig()
