"""
Logging utilities for DebugTutor application
"""
import logging
import os
import sys
from datetime import datetime
from typing import Optional
import streamlit as st

class AppLogger:
    """Custom logger for the application"""
    
    def __init__(self, name: str = "debugtutor", log_level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, log_level.upper()))
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup logging handlers"""
        # Create logs directory if it doesn't exist
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # File handler
        log_file = os.path.join(log_dir, f"debugtutor_{datetime.now().strftime('%Y%m%d')}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message: str, extra: Optional[dict] = None):
        """Log info message"""
        self.logger.info(message, extra=extra or {})
    
    def warning(self, message: str, extra: Optional[dict] = None):
        """Log warning message"""
        self.logger.warning(message, extra=extra or {})
    
    def error(self, message: str, extra: Optional[dict] = None):
        """Log error message"""
        self.logger.error(message, extra=extra or {})
    
    def debug(self, message: str, extra: Optional[dict] = None):
        """Log debug message"""
        self.logger.debug(message, extra=extra or {})

class StreamlitLogger:
    """Logger that integrates with Streamlit UI"""
    
    def __init__(self):
        self.app_logger = AppLogger()
    
    def log_user_action(self, action: str, details: dict = None):
        """Log user actions"""
        details = details or {}
        message = f"User action: {action}"
        self.app_logger.info(message, extra=details)
    
    def log_error(self, error: Exception, context: str = ""):
        """Log errors with context"""
        message = f"Error in {context}: {str(error)}"
        self.app_logger.error(message, extra={"error_type": type(error).__name__})
        
        # Show user-friendly error in UI
        if "api" in context.lower():
            st.error("🔌 API connection issue. Please check your internet connection.")
        elif "parsing" in context.lower():
            st.error("📝 Code parsing failed. Please check your code syntax.")
        else:
            st.error(f"❌ An error occurred: {str(error)}")
    
    def log_performance(self, operation: str, duration: float):
        """Log performance metrics"""
        message = f"Performance: {operation} took {duration:.2f}s"
        self.app_logger.info(message, extra={"operation": operation, "duration": duration})
        
        # Show performance warning if slow
        if duration > 10:
            st.warning(f"⏱️ {operation} is taking longer than usual ({duration:.1f}s)")

# Global logger instance
app_logger = StreamlitLogger()
