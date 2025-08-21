"""
Supabase Authentication module for DebugTutor
Handles Google OAuth authentication and user session management
"""
import streamlit as st
import os
from supabase import create_client, Client
from typing import Optional, Dict, Any
import json
from logger import app_logger

class SupabaseAuth:
    """Handles Supabase authentication with Google OAuth"""
    
    def __init__(self):
        self.supabase: Optional[Client] = None
        self.initialize_client()
    
    def initialize_client(self):
        """Initialize Supabase client"""
        try:
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_ANON_KEY')
            
            if not supabase_url or not supabase_key:
                st.error("🔴 Supabase credentials not configured. Please add SUPABASE_URL and SUPABASE_ANON_KEY to your .env file")
                return
            
            self.supabase = create_client(supabase_url, supabase_key)
            app_logger.log_user_action("supabase_initialized")
            
        except Exception as e:
            app_logger.log_error(e, "supabase_initialization")
            st.error(f"❌ Failed to initialize Supabase: {str(e)}")
    
    def is_configured(self) -> bool:
        """Check if Supabase is properly configured"""
        return self.supabase is not None
    
    def get_google_auth_url(self) -> Optional[str]:
        """Get Google OAuth URL for authentication"""
        if not self.supabase:
            return None
        
        try:
            # Get the current URL for redirect
            redirect_url = os.getenv("REDIRECT_URL", "http://localhost:8501")
            
            response = self.supabase.auth.sign_in_with_oauth({
                "provider": "google",
                "options": {
                    "redirect_to": redirect_url
                }
            })
            
            return response.url
            
        except Exception as e:
            app_logger.log_error(e, "google_auth_url")
            st.error(f"❌ Failed to get Google auth URL: {str(e)}")
            return None
    
    def handle_oauth_callback(self, code: str) -> bool:
        """Handle OAuth callback and set session"""
        if not self.supabase:
            return False
        
        try:
            # Exchange code for session
            response = self.supabase.auth.exchange_code_for_session({
                "auth_code": code
            })
            
            if response.user:
                self.set_user_session(response.user, response.session)
                app_logger.log_user_action("user_authenticated", {"user_id": response.user.id})
                return True
            
            return False
            
        except Exception as e:
            app_logger.log_error(e, "oauth_callback")
            st.error(f"❌ Authentication failed: {str(e)}")
            return False
    
    def set_user_session(self, user: Any, session: Any):
        """Set user session in Streamlit state"""
        st.session_state.authenticated = True
        st.session_state.user = {
            'id': user.id,
            'email': user.email,
            'name': user.user_metadata.get('full_name', user.email),
            'avatar_url': user.user_metadata.get('avatar_url', ''),
            'provider': 'google'
        }
        st.session_state.auth_session = session
    
    def sign_out(self):
        """Sign out user and clear session"""
        try:
            if self.supabase:
                self.supabase.auth.sign_out()
            
            # Clear session state
            st.session_state.authenticated = False
            st.session_state.user = None
            st.session_state.auth_session = None
            
            app_logger.log_user_action("user_signed_out")
            
        except Exception as e:
            app_logger.log_error(e, "sign_out")
            st.error(f"❌ Sign out failed: {str(e)}")
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """Get current authenticated user"""
        return st.session_state.get('user')
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return st.session_state.get('authenticated', False)
    
    def refresh_session(self):
        """Refresh the current session"""
        if not self.supabase or not st.session_state.get('auth_session'):
            return
        
        try:
            response = self.supabase.auth.refresh_session(st.session_state.auth_session)
            if response.session:
                st.session_state.auth_session = response.session
                
        except Exception as e:
            app_logger.log_error(e, "refresh_session")
            # If refresh fails, sign out user
            self.sign_out()

# Global auth instance
auth_manager = SupabaseAuth()
