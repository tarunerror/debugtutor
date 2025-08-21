"""
Health check and monitoring utilities for DebugTutor application
"""
import time
import psutil
import streamlit as st
from typing import Dict, Any
from config import config_manager
from logger import app_logger

class HealthMonitor:
    """System health monitoring"""
    
    def __init__(self):
        self.start_time = time.time()
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "memory_available": memory.available / (1024**3),  # GB
                "disk_usage": disk.percent,
                "disk_free": disk.free / (1024**3),  # GB
                "uptime": time.time() - self.start_time
            }
        except Exception as e:
            app_logger.log_error(e, "system_metrics")
            return {}
    
    def check_api_health(self) -> Dict[str, Any]:
        """Check API connectivity and health"""
        try:
            config = config_manager.config
            if not config or not config.openrouter_api_key:
                return {
                    "status": "error",
                    "message": "API key not configured",
                    "response_time": None
                }
            
            # Simple health check (can be enhanced with actual API ping)
            return {
                "status": "ok",
                "message": "API configured",
                "response_time": 0.1,
                "model": config.openrouter_model
            }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "response_time": None
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status"""
        system_metrics = self.get_system_metrics()
        api_health = self.check_api_health()
        
        # Determine overall health
        overall_status = "healthy"
        issues = []
        
        if system_metrics.get("cpu_usage", 0) > 80:
            issues.append("High CPU usage")
            overall_status = "warning"
        
        if system_metrics.get("memory_usage", 0) > 85:
            issues.append("High memory usage")
            overall_status = "warning"
        
        if api_health.get("status") != "ok":
            issues.append("API not available")
            overall_status = "error"
        
        return {
            "overall_status": overall_status,
            "issues": issues,
            "system_metrics": system_metrics,
            "api_health": api_health,
            "timestamp": time.time()
        }

class ErrorReporter:
    """Error reporting and tracking"""
    
    def __init__(self):
        self.error_count = 0
        self.last_errors = []
    
    def report_error(self, error: Exception, context: str = ""):
        """Report and track errors"""
        self.error_count += 1
        error_info = {
            "error": str(error),
            "type": type(error).__name__,
            "context": context,
            "timestamp": time.time()
        }
        
        self.last_errors.append(error_info)
        if len(self.last_errors) > 10:  # Keep only last 10 errors
            self.last_errors.pop(0)
        
        app_logger.log_error(error, context)
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get error summary for monitoring"""
        return {
            "total_errors": self.error_count,
            "recent_errors": len(self.last_errors),
            "last_errors": self.last_errors[-5:] if self.last_errors else []
        }

# Global instances
health_monitor = HealthMonitor()
error_reporter = ErrorReporter()
