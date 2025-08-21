"""
Enhanced UI components for DebugTutor application
"""
import streamlit as st
from typing import Dict, Any, List, Optional
import time
from datetime import datetime
from analytics import session_analytics, usage_metrics
from logger import app_logger

class ModernUI:
    """Modern UI components and styling"""
    
    @staticmethod
    def inject_custom_css():
        """Inject enhanced custom CSS"""
        st.markdown("""
        <style>
            /* Import Google Fonts */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
            
            /* Global Styles */
            .stApp {
                font-family: 'Inter', sans-serif;
            }
            
            /* Header Styles */
            .main-header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 2rem;
                border-radius: 15px;
                color: white;
                text-align: center;
                margin-bottom: 2rem;
                box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
                backdrop-filter: blur(10px);
            }
            
            .main-header h1 {
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 0.5rem;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            }
            
            .main-header p {
                font-size: 1.2rem;
                opacity: 0.9;
                font-weight: 300;
            }
            
            /* Status Cards */
            .status-card {
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                border: 1px solid #e8ecf3;
                margin: 1rem 0;
                transition: transform 0.2s ease, box-shadow 0.2s ease;
            }
            
            .status-card:hover {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(0,0,0,0.15);
            }
            
            .status-card.success {
                border-left: 5px solid #10b981;
                background: linear-gradient(135deg, #ecfdf5 0%, #f0fdf4 100%);
            }
            
            .status-card.warning {
                border-left: 5px solid #f59e0b;
                background: linear-gradient(135deg, #fffbeb 0%, #fefce8 100%);
            }
            
            .status-card.error {
                border-left: 5px solid #ef4444;
                background: linear-gradient(135deg, #fef2f2 0%, #fef1f1 100%);
            }
            
            /* Code Container */
            .code-container {
                background: #1e293b;
                border: 1px solid #334155;
                border-radius: 12px;
                padding: 1.5rem;
                margin: 1rem 0;
                position: relative;
                overflow-x: auto;
            }
            
            .code-container::before {
                content: "";
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                height: 3px;
                background: linear-gradient(90deg, #667eea, #764ba2);
                border-radius: 12px 12px 0 0;
            }
            
            /* Action Buttons */
            .action-button {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                padding: 0.75rem 1.5rem;
                border-radius: 8px;
                font-weight: 500;
                cursor: pointer;
                transition: all 0.2s ease;
                box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
            }
            
            .action-button:hover {
                transform: translateY(-1px);
                box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
            }
            
            /* Chat Messages */
            .chat-message {
                padding: 1.5rem;
                margin: 1rem 0;
                border-radius: 12px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                animation: fadeIn 0.3s ease-in;
            }
            
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .user-message {
                background: linear-gradient(135deg, #dbeafe 0%, #e0f2fe 100%);
                border-left: 4px solid #3b82f6;
                margin-left: 0;
                margin-right: 0;
            }
            
            .assistant-message {
                background: linear-gradient(135deg, #f3e8ff 0%, #faf5ff 100%);
                border-left: 4px solid #8b5cf6;
                margin-left: 0;
                margin-right: 0;
            }
            
            /* Metrics Dashboard */
            .metrics-card {
                background: white;
                padding: 1.5rem;
                border-radius: 12px;
                text-align: center;
                box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                border: 1px solid #e8ecf3;
            }
            
            .metrics-number {
                font-size: 2rem;
                font-weight: 700;
                color: #667eea;
                margin-bottom: 0.5rem;
            }
            
            .metrics-label {
                color: #6b7280;
                font-size: 0.9rem;
                font-weight: 500;
            }
            
            /* Sidebar Enhancements */
            .sidebar-section {
                background: white;
                padding: 1rem;
                border-radius: 8px;
                margin: 1rem 0;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            /* Loading Animation */
            .loading-spinner {
                display: inline-block;
                width: 20px;
                height: 20px;
                border: 3px solid #f3f3f3;
                border-top: 3px solid #667eea;
                border-radius: 50%;
                animation: spin 1s linear infinite;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            
            /* Responsive Design */
            @media (max-width: 768px) {
                .main-header h1 { font-size: 2rem; }
                .main-header p { font-size: 1rem; }
                .chat-message { margin-left: 0; margin-right: 0; }
            }
        </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def display_status_card(title: str, content: str, status: str = "info", icon: str = "ℹ️"):
        """Display a modern status card"""
        status_class = f"status-card {status}"
        st.markdown(f"""
        <div class="{status_class}">
            <h4>{icon} {title}</h4>
            <p>{content}</p>
        </div>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def display_metrics_dashboard():
        """Display analytics dashboard"""
        st.markdown("### 📊 Session Analytics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        summary = session_analytics.get_session_summary()
        metrics = usage_metrics.get_metrics_summary()
        
        with col1:
            st.markdown(f"""
            <div class="metrics-card">
                <div class="metrics-number">{summary['actions_count']}</div>
                <div class="metrics-label">Actions</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metrics-card">
                <div class="metrics-number">{summary['errors_fixed']}</div>
                <div class="metrics-label">Errors Fixed</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metrics-card">
                <div class="metrics-number">{len(summary['languages_used'])}</div>
                <div class="metrics-label">Languages</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metrics-card">
                <div class="metrics-number">{summary['session_duration_minutes']}</div>
                <div class="metrics-label">Minutes</div>
            </div>
            """, unsafe_allow_html=True)

class AdvancedComponents:
    """Advanced UI components for production features"""
    
    @staticmethod
    def display_system_health():
        """Display system health indicators"""
        from config import config_manager
        
        st.markdown("### 🔧 System Status")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # API Status
            if config_manager.is_valid():
                ModernUI.display_status_card(
                    "API Connection", 
                    "OpenRouter API configured and ready", 
                    "success", 
                    "✅"
                )
            else:
                ModernUI.display_status_card(
                    "API Connection", 
                    "API key not configured", 
                    "error", 
                    "❌"
                )
        
        with col2:
            # Session Status
            if 'conversation_history' in st.session_state and st.session_state.conversation_history:
                ModernUI.display_status_card(
                    "Session Active", 
                    f"{len(st.session_state.conversation_history)} messages", 
                    "success", 
                    "💬"
                )
            else:
                ModernUI.display_status_card(
                    "Session", 
                    "Ready to start debugging", 
                    "info", 
                    "🚀"
                )
    
    @staticmethod
    def display_feature_showcase():
        """Display feature showcase in sidebar"""
        st.markdown("### ✨ Features")
        
        features = [
            ("🔍", "Smart Analysis", "AI-powered code analysis"),
            ("🔧", "Auto-Fix", "Intelligent error correction"),
            ("💬", "Interactive Chat", "Ask follow-up questions"),
            ("📊", "Analytics", "Track your progress"),
            ("🌐", "Multi-Language", "Support for 7+ languages"),
            ("📱", "PWA Ready", "Install as mobile app")
        ]
        
        for icon, title, desc in features:
            st.markdown(f"""
            <div style="padding: 0.5rem; margin: 0.5rem 0; border-left: 3px solid #667eea;">
                <strong>{icon} {title}</strong><br>
                <small style="color: #6b7280;">{desc}</small>
            </div>
            """, unsafe_allow_html=True)
    
    @staticmethod
    def display_quick_tips():
        """Display quick tips for users"""
        st.markdown("### 💡 Quick Tips")
        
        tips = [
            "Start with simple syntax errors",
            "Use specific error descriptions",
            "Ask follow-up questions for clarity",
            "Try different programming languages",
            "Check the analytics dashboard"
        ]
        
        for i, tip in enumerate(tips, 1):
            st.markdown(f"**{i}.** {tip}")
    
    @staticmethod
    def display_performance_monitor():
        """Display performance monitoring"""
        if st.checkbox("🔍 Show Performance Monitor", key="perf_monitor"):
            st.markdown("### ⚡ Performance")
            
            # Session metrics
            summary = session_analytics.get_session_summary()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Actions/Min", f"{summary['avg_actions_per_minute']:.1f}")
            with col2:
                st.metric("Session Time", f"{summary['session_duration_minutes']:.1f}m")
            
            # Show recent actions
            if 'analytics' in st.session_state:
                st.markdown("**Recent Actions:**")
                recent_actions = list(st.session_state.analytics.values())[-5:]
                for action in recent_actions:
                    st.text(f"• {action['type']} ({action.get('language', 'N/A')})")

class GitHubComponents:
    """GitHub-related UI components"""
    
    @staticmethod
    def display_github_button(repo_url: str = "https://github.com/your-username/debugtutor"):
        """Display GitHub repository button"""
        st.markdown("""
        <style>
        .github-button {
            background: linear-gradient(135deg, #24292e 0%, #1a1e22 100%);
            color: white;
            border: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 4px 15px rgba(36, 41, 46, 0.3);
            text-decoration: none;
            display: inline-flex;
            align-items: center;
            gap: 0.5rem;
        }
        
        .github-button:hover {
            transform: translateY(-1px);
            box-shadow: 0 6px 20px rgba(36, 41, 46, 0.4);
            background: linear-gradient(135deg, #2f363d 0%, #24292e 100%);
        }
        
        .github-icon {
            width: 20px;
            height: 20px;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # GitHub button with icon
        st.markdown(f"""
        <a href="{repo_url}" target="_blank" class="github-button">
            <svg class="github-icon" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
            </svg>
            View on GitHub
        </a>
        """, unsafe_allow_html=True)

class AuthComponents:
    """Authentication-related UI components"""
    
    @staticmethod
    def display_sign_in_button():
        """Display Google Sign In button"""
        st.markdown("""
        <div style="text-align: center; padding: 2rem;">
            <h3>🔐 Sign In Required</h3>
            <p>Please sign in with your Google account to access DebugTutor</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔑 Sign In with Google", type="primary", use_container_width=True):
                return True
        return False
    
    @staticmethod
    def display_user_profile(user: Dict[str, Any]):
        """Display user profile section"""
        st.markdown("### 👤 User Profile")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            if user.get('avatar_url'):
                st.image(user['avatar_url'], width=80)
            else:
                st.markdown("""
                <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                           border-radius: 50%; display: flex; align-items: center; justify-content: center; 
                           color: white; font-size: 2rem; font-weight: bold;">
                    {initial}
                </div>
                """.format(initial=user.get('name', 'U')[0].upper()), unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="status-card">
                <h4>👋 Welcome, {user.get('name', 'User')}!</h4>
                <p><strong>Email:</strong> {user.get('email', 'N/A')}</p>
                <p><strong>Provider:</strong> {user.get('provider', 'Google').title()}</p>
            </div>
            """, unsafe_allow_html=True)
        
        if st.button("🚪 Sign Out", type="secondary"):
            return True
        return False
    
    @staticmethod
    def display_auth_status():
        """Display authentication status in sidebar"""
        from auth import auth_manager
        
        if auth_manager.is_authenticated():
            user = auth_manager.get_current_user()
            st.sidebar.markdown("### 👤 Signed In")
            st.sidebar.markdown(f"**{user.get('name', 'User')}**")
            st.sidebar.markdown(f"_{user.get('email', 'N/A')}_")
            
            if st.sidebar.button("🚪 Sign Out", key="sidebar_signout"):
                auth_manager.sign_out()
                st.rerun()
        else:
            st.sidebar.markdown("### 🔐 Authentication")
            st.sidebar.info("Sign in to access all features")

def track_user_action(action_type: str, language: str = None, code_lines: int = 0):
    """Helper function to track user actions"""
    session_analytics.track_action(action_type, language, code_lines)
    usage_metrics.record_usage(action_type, language)
    app_logger.log_user_action(action_type, {
        "language": language,
        "code_lines": code_lines,
        "timestamp": datetime.now().isoformat()
    })
