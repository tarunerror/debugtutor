"""
Deployment utilities and production configuration for DebugTutor
"""
import os
import json
from typing import Dict, Any
import streamlit as st

class DeploymentConfig:
    """Deployment configuration management"""
    
    def __init__(self):
        self.env = os.getenv("ENVIRONMENT", "development")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
    
    def get_config(self) -> Dict[str, Any]:
        """Get deployment-specific configuration"""
        base_config = {
            "app_name": "DebugTutor",
            "version": "2.0.0",
            "environment": self.env,
            "debug": self.debug
        }
        
        if self.env == "production":
            return {
                **base_config,
                "log_level": "INFO",
                "enable_analytics": True,
                "enable_error_reporting": True,
                "rate_limiting": True,
                "cache_ttl": 3600
            }
        elif self.env == "staging":
            return {
                **base_config,
                "log_level": "DEBUG",
                "enable_analytics": True,
                "enable_error_reporting": True,
                "rate_limiting": False,
                "cache_ttl": 300
            }
        else:  # development
            return {
                **base_config,
                "log_level": "DEBUG",
                "enable_analytics": False,
                "enable_error_reporting": False,
                "rate_limiting": False,
                "cache_ttl": 60
            }
    
    def setup_production_settings(self):
        """Configure Streamlit for production"""
        if self.env == "production":
            # Production optimizations
            st.set_page_config(
                page_title="DebugTutor - AI Code Debugging Assistant",
                page_icon="🐛",
                layout="wide",
                initial_sidebar_state="expanded",
                menu_items={
                    'Get Help': 'https://debugtutor.ai/help',
                    'Report a bug': 'https://debugtutor.ai/issues',
                    'About': 'DebugTutor v2.0 - Professional AI debugging assistant'
                }
            )

class ProductionOptimizer:
    """Production performance optimizations"""
    
    @staticmethod
    def setup_caching():
        """Setup Streamlit caching for production"""
        
        @st.cache_data(ttl=3600)
        def cache_static_data(data_key: str):
            """Cache static application data"""
            return data_key
        
        @st.cache_resource
        def load_models():
            """Cache model loading"""
            from parser import CodeParser
            from llm_utils import LLMProcessor
            return CodeParser(), LLMProcessor()
    
    @staticmethod
    def optimize_ui():
        """UI optimizations for production"""
        # Reduce unnecessary reruns
        if 'optimization_applied' not in st.session_state:
            st.session_state.optimization_applied = True
            
            # Set up efficient session state management
            if 'ui_state' not in st.session_state:
                st.session_state.ui_state = {
                    'last_update': 0,
                    'cache_version': 1
                }

# Global deployment config
deployment_config = DeploymentConfig()
