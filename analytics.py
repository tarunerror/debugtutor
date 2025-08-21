"""
Analytics and metrics tracking for DebugTutor application
"""
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import streamlit as st
import json
import os

class SessionAnalytics:
    """Track user session analytics"""
    
    def __init__(self):
        self.session_start = time.time()
        self.actions_count = 0
        self.errors_fixed = 0
        self.languages_used = set()
        self.total_code_lines = 0
        
    def track_action(self, action_type: str, language: str = None, code_lines: int = 0):
        """Track user actions"""
        self.actions_count += 1
        if language:
            self.languages_used.add(language)
        if code_lines:
            self.total_code_lines += code_lines
            
        # Store in session state for persistence
        if 'analytics' not in st.session_state:
            st.session_state.analytics = {}
        
        st.session_state.analytics[f"action_{self.actions_count}"] = {
            "type": action_type,
            "timestamp": datetime.now().isoformat(),
            "language": language,
            "code_lines": code_lines
        }
    
    def track_error_fixed(self):
        """Track when an error is successfully fixed"""
        self.errors_fixed += 1
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get session analytics summary"""
        session_duration = time.time() - self.session_start
        return {
            "session_duration_minutes": round(session_duration / 60, 2),
            "actions_count": self.actions_count,
            "errors_fixed": self.errors_fixed,
            "languages_used": list(self.languages_used),
            "total_code_lines": self.total_code_lines,
            "avg_actions_per_minute": round(self.actions_count / (session_duration / 60), 2) if session_duration > 60 else 0
        }

class UsageMetrics:
    """Track application usage metrics"""
    
    def __init__(self):
        self.metrics_file = "logs/usage_metrics.json"
        self._ensure_metrics_file()
    
    def _ensure_metrics_file(self):
        """Ensure metrics file exists"""
        os.makedirs("logs", exist_ok=True)
        if not os.path.exists(self.metrics_file):
            with open(self.metrics_file, 'w') as f:
                json.dump({"daily_metrics": {}, "total_metrics": {}}, f)
    
    def record_usage(self, action: str, language: str = None):
        """Record usage metrics"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            with open(self.metrics_file, 'r') as f:
                data = json.load(f)
            
            # Initialize today's metrics if not exists
            if today not in data["daily_metrics"]:
                data["daily_metrics"][today] = {
                    "sessions": 0,
                    "actions": {},
                    "languages": {}
                }
            
            # Update metrics
            if action not in data["daily_metrics"][today]["actions"]:
                data["daily_metrics"][today]["actions"][action] = 0
            data["daily_metrics"][today]["actions"][action] += 1
            
            if language:
                if language not in data["daily_metrics"][today]["languages"]:
                    data["daily_metrics"][today]["languages"][language] = 0
                data["daily_metrics"][today]["languages"][language] += 1
            
            # Update total metrics
            if "total_actions" not in data["total_metrics"]:
                data["total_metrics"]["total_actions"] = 0
            data["total_metrics"]["total_actions"] += 1
            
            with open(self.metrics_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            # Fail silently for metrics to not disrupt user experience
            pass
    
    def get_metrics_summary(self) -> Dict[str, Any]:
        """Get metrics summary for display"""
        try:
            with open(self.metrics_file, 'r') as f:
                data = json.load(f)
            
            # Get last 7 days
            last_7_days = []
            for i in range(7):
                date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                last_7_days.append(date)
            
            weekly_actions = sum(
                sum(data["daily_metrics"].get(date, {}).get("actions", {}).values())
                for date in last_7_days
            )
            
            return {
                "total_actions": data["total_metrics"].get("total_actions", 0),
                "weekly_actions": weekly_actions,
                "days_tracked": len(data["daily_metrics"])
            }
        except:
            return {"total_actions": 0, "weekly_actions": 0, "days_tracked": 0}

# Global analytics instances
session_analytics = SessionAnalytics()
usage_metrics = UsageMetrics()
