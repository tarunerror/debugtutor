"""
Configuration management for DebugTutor application
"""
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

@dataclass
class AppConfig:
    """Application configuration class"""
    # API Configuration
    openrouter_api_key: str
    openrouter_model: str = "deepseek/deepseek-r1-distill-llama-70b:free"
    openrouter_base_url: str = "https://openrouter.ai/api/v1/chat/completions"
    
    # App Configuration
    app_name: str = "DebugTutor"
    app_version: str = "2.0.0"
    debug_mode: bool = False
    max_conversation_history: int = 50
    
    # UI Configuration
    theme: str = "light"
    enable_analytics: bool = True
    enable_error_reporting: bool = True
    
    # Performance Configuration
    request_timeout: int = 30
    max_code_length: int = 10000
    rate_limit_per_minute: int = 60

class ConfigManager:
    """Manages application configuration and validation"""
    
    def __init__(self):
        self._config: Optional[AppConfig] = None
        self._load_config()
    
    def _load_config(self) -> None:
        """Load configuration from environment variables"""
        try:
            api_key = os.getenv("OPENROUTER_API_KEY")
            if not api_key:
                st.error("⚠️ OPENROUTER_API_KEY not found in environment variables")
                st.info("Please add your API key to the .env file")
                return
            
            self._config = AppConfig(
                openrouter_api_key=api_key,
                openrouter_model=os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-r1-distill-llama-70b:free"),
                openrouter_base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1/chat/completions"),
                debug_mode=os.getenv("DEBUG_MODE", "false").lower() == "true",
                max_conversation_history=int(os.getenv("MAX_CONVERSATION_HISTORY", "50")),
                theme=os.getenv("THEME", "light"),
                enable_analytics=os.getenv("ENABLE_ANALYTICS", "true").lower() == "true",
                enable_error_reporting=os.getenv("ENABLE_ERROR_REPORTING", "true").lower() == "true",
                request_timeout=int(os.getenv("REQUEST_TIMEOUT", "30")),
                max_code_length=int(os.getenv("MAX_CODE_LENGTH", "10000")),
                rate_limit_per_minute=int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
            )
            
        except Exception as e:
            st.error(f"Error loading configuration: {str(e)}")
            self._config = None
    
    @property
    def config(self) -> Optional[AppConfig]:
        """Get the current configuration"""
        return self._config
    
    def is_valid(self) -> bool:
        """Check if configuration is valid"""
        return self._config is not None and bool(self._config.openrouter_api_key)
    
    def get_status(self) -> Dict[str, Any]:
        """Get configuration status for debugging"""
        if not self._config:
            return {"status": "error", "message": "Configuration not loaded"}
        
        return {
            "status": "ok",
            "api_key_configured": bool(self._config.openrouter_api_key),
            "model": self._config.openrouter_model,
            "debug_mode": self._config.debug_mode,
            "version": self._config.app_version
        }

# Global configuration instance
config_manager = ConfigManager()
