import streamlit as st
import os
from typing import Optional, Dict, Any
import json
import time
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
from parser import CodeParser
from llm_utils import LLMProcessor
from config import config_manager
from logger import app_logger
from ui_components import ModernUI, AdvancedComponents, AuthComponents, GitHubComponents, track_user_action
from analytics import session_analytics
from auth import auth_manager

# Configure Streamlit page
st.set_page_config(
    page_title="DebugTutor - AI Code Debugging Assistant",
    page_icon="🐛",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': None
    }
)

# Inject modern CSS
ModernUI.inject_custom_css()

# Initialize session state
if 'conversation_history' not in st.session_state:
    st.session_state.conversation_history = []
if 'parsed_code' not in st.session_state:
    st.session_state.parsed_code = None
if 'current_code' not in st.session_state:
    st.session_state.current_code = ""

def initialize_components():
    """Initialize the code parser and LLM processor"""
    if 'parser' not in st.session_state:
        st.session_state.parser = CodeParser()
    if 'llm_processor' not in st.session_state:
        st.session_state.llm_processor = LLMProcessor()

def display_header():
    """Display the enhanced main header"""
    config = config_manager.config
    version = config.app_version if config else "2.0.0"
    
    st.markdown(f"""
    <div class="main-header">
        <h1>🐛 DebugTutor</h1>
        <p style="font-size: 0.9rem; opacity: 0.8; font-weight: bold;">Code with confidence, debug with intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Show system status only if API is not configured
    if not config_manager.is_valid():
        st.error("🔴 Please configure your OpenRouter API key in the .env file")
        st.info("💡 Get your free API key from [OpenRouter](https://openrouter.ai/settings/keys)")

def display_code_input():
    """Display enhanced code input section"""
    st.header("📝 Code Input")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        # Language selector with icons
        languages = {
            "python": "🐍 Python",
            "javascript": "🟨 JavaScript", 
            "typescript": "🔷 TypeScript",
            "cpp": "⚡ C++",
            "java": "☕ Java",
            "go": "🐹 Go",
            "rust": "🦀 Rust"
        }
        
        selected_language = st.selectbox(
            "Select Programming Language:",
            list(languages.keys()),
            format_func=lambda x: languages[x],
            index=0,
            key="language_selector"
        )
    
    with col2:
        st.write("")  # Spacer
        st.write("")  # Spacer
        clear_code = st.button("🗑️ Clear All", type="secondary", use_container_width=True)
    
    with col3:
        st.write("")  # Spacer
        st.write("")  # Spacer
        example_code = st.button("📋 Load Example", type="secondary", use_container_width=True)
    
    # Load example code
    if example_code:
        examples = {
            "python": "def calculate_average(numbers)\n    total = 0\n    for num in numbers:\n        total += num\n    return total / len(numbers)\n\nresult = calculate_average([1, 2, 3, 4, 5])\nprint(\"Average:\", result",
            "javascript": "function calculateSum(arr) {\n    let sum = 0\n    for (let i = 0; i <= arr.length; i++) {\n        sum += arr[i];\n    }\n    return sum\n}\n\nconsole.log(calculateSum([1, 2, 3, 4, 5]));",
            "cpp": "#include <iostream>\nusing namespace std;\n\nint main() {\n    int arr[] = {1, 2, 3, 4, 5}\n    int sum = 0;\n    \n    for (int i = 0; i <= 5; i++) {\n        sum += arr[i];\n    }\n    \n    cout << \"Sum: \" << sum << endl;\n    return 0;\n}"
        }
        st.session_state.current_code = examples.get(selected_language, examples["python"])
        st.rerun()
    
    # Code input area with enhanced styling
    code_input = st.text_area(
        "Paste your buggy code here:",
        height=350,
        placeholder=f"Enter your {languages[selected_language]} code that needs debugging...\n\n💡 Tip: Start with simple syntax errors for best results!",
        key="code_input",
        value=st.session_state.current_code,
        help="Paste your code here and our AI will help you debug it step by step."
    )
    
    # Code statistics
    if code_input.strip():
        lines = len(code_input.split('\n'))
        chars = len(code_input)
        st.caption(f"📊 {lines} lines, {chars} characters")
        
        # Track code input
        track_user_action("code_input", selected_language, lines)
    
    if clear_code:
        st.session_state.current_code = ""
        st.session_state.parsed_code = None
        st.session_state.conversation_history = []
        track_user_action("clear_code")
        st.rerun()
    
    if code_input != st.session_state.current_code:
        st.session_state.current_code = code_input
        st.session_state.parsed_code = None
    
    return code_input, selected_language

def display_parsing_results(parsed_result: Dict[str, Any]):
    """Display enhanced code parsing results"""
    if not parsed_result:
        return
    
    st.header("🔍 Code Analysis")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if parsed_result.get('syntax_errors'):
            st.markdown("### ❌ Syntax Errors Detected")
            for i, error in enumerate(parsed_result['syntax_errors'], 1):
                ModernUI.display_status_card(
                    f"Error #{i}",
                    f"Line {error.get('line', 'Unknown')}: {error.get('message', 'Syntax error detected')}",
                    "error",
                    "🚨"
                )
        else:
            ModernUI.display_status_card(
                "Syntax Check",
                "No syntax errors detected - code structure looks good!",
                "success",
                "✅"
            )
        
        if parsed_result.get('warnings'):
            st.markdown("### ⚠️ Potential Issues")
            for i, warning in enumerate(parsed_result['warnings'], 1):
                ModernUI.display_status_card(
                    f"Warning #{i}",
                    f"Line {warning.get('line', 'Unknown')}: {warning.get('message', 'Potential issue detected')}",
                    "warning",
                    "⚠️"
                )
    
    with col2:
        # Analysis summary
        error_count = len(parsed_result.get('syntax_errors', []))
        warning_count = len(parsed_result.get('warnings', []))
        
        st.markdown("### 📊 Summary")
        st.metric("Syntax Errors", error_count, delta=None if error_count == 0 else f"+{error_count}")
        st.metric("Warnings", warning_count, delta=None if warning_count == 0 else f"+{warning_count}")
        
        if error_count == 0 and warning_count == 0:
            st.success("🎉 Code looks clean!")
        elif error_count > 0:
            st.error("🔧 Needs fixing")
        else:
            st.warning("⚠️ Minor issues")

def display_action_buttons(code_input: str, language: str):
    """Display enhanced action buttons"""
    st.header("🚀 AI Actions")
    
    # Check if API is configured
    api_ready = config_manager.is_valid()
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        explain_error = st.button(
            "🔍 Explain Error", 
            type="primary", 
            use_container_width=True,
            disabled=not api_ready,
            help="Get detailed explanations of errors in your code"
        )
    
    with col2:
        suggest_fix = st.button(
            "🔧 Suggest Fix", 
            type="primary", 
            use_container_width=True,
            disabled=not api_ready,
            help="Get corrected code with explanations"
        )
    
    with col3:
        analyze_code = st.button(
            "📊 Analyze Code", 
            type="secondary", 
            use_container_width=True,
            disabled=not api_ready,
            help="Get code quality feedback and best practices"
        )
    
    with col4:
        optimize_code = st.button(
            "⚡ Optimize", 
            type="secondary", 
            use_container_width=True,
            disabled=not api_ready,
            help="Get performance optimization suggestions"
        )
    
    if not api_ready:
        st.warning("⚠️ Configure your OpenRouter API key to use AI features")
    
    return explain_error, suggest_fix, analyze_code, optimize_code

def display_conversation():
    """Display conversation history"""
    if st.session_state.conversation_history:
        st.header("💬 Conversation")
        
        for i, message in enumerate(st.session_state.conversation_history):
            if message['role'] == 'user':
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>You:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>DebugTutor:</strong> {message['content']}
                </div>
                """, unsafe_allow_html=True)

def display_follow_up():
    """Display follow-up question input"""
    if st.session_state.conversation_history:
        st.header("❓ Ask Follow-up Questions")
        
        follow_up = st.text_input(
            "Ask a follow-up question about your code:",
            placeholder="e.g., 'Can you explain this error in simpler terms?'"
        )
        
        if st.button("Send Question", type="primary"):
            if follow_up.strip():
                # Add user question to conversation
                st.session_state.conversation_history.append({
                    'role': 'user',
                    'content': follow_up
                })
                
                # Process follow-up question with streaming
                response_placeholder = st.empty()
                full_response = ""
                
                try:
                    start_time = time.time()
                    track_user_action("follow_up_question")
                    
                    with st.spinner("💭 Processing question..."):
                        for chunk in st.session_state.llm_processor.process_follow_up_stream(
                            follow_up,
                            st.session_state.current_code,
                            st.session_state.conversation_history
                        ):
                            full_response += chunk
                            response_placeholder.markdown(f"**DebugTutor:** {full_response}▊")
                    
                    # Final update without cursor
                    response_placeholder.markdown(f"**DebugTutor:** {full_response}")
                    
                    st.session_state.conversation_history.append({
                        'role': 'assistant',
                        'content': full_response
                    })
                    
                    # Log performance
                    duration = time.time() - start_time
                    app_logger.log_performance("follow_up_question", duration)
                    
                    st.rerun()
                    
                except Exception as e:
                    app_logger.log_error(e, "follow_up_question")
                    st.error(f"❌ Error processing follow-up: {str(e)}")

def handle_authentication():
    """Handle authentication flow"""
    # Check for OAuth callback parameters
    query_params = st.query_params
    
    if 'code' in query_params and not auth_manager.is_authenticated():
        code = query_params['code']
        if auth_manager.handle_oauth_callback(code):
            st.success("✅ Successfully signed in!")
            st.query_params.clear()  # Clear URL parameters
            st.rerun()
    
    # Handle sign in button click
    if not auth_manager.is_authenticated():
        if AuthComponents.display_sign_in_button():
            auth_url = auth_manager.get_google_auth_url()
            if auth_url:
                st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}">', unsafe_allow_html=True)
                st.info("Redirecting to Google for authentication...")
            else:
                st.error("❌ Failed to initiate Google authentication. Please check your Supabase configuration.")
        return False
    
    return True

def display_user_profile_section():
    """Display user profile section if authenticated"""
    if auth_manager.is_authenticated():
        user = auth_manager.get_current_user()
        st.markdown("---")
        
        with st.expander("👤 User Profile", expanded=False):
            if AuthComponents.display_user_profile(user):
                auth_manager.sign_out()
                st.rerun()

def main():
    """Main application function"""
    initialize_components()
    display_header()
    
    # Handle authentication
    if not handle_authentication():
        return
    
    # Enhanced Sidebar
    with st.sidebar:
        # Authentication status
        AuthComponents.display_auth_status()
        
        st.markdown("---")
        
        # Feature Showcase
        AdvancedComponents.display_feature_showcase()
        
        st.markdown("---")
        
        # Quick Tips
        AdvancedComponents.display_quick_tips()
        
        st.markdown("---")
        
        # Performance Monitor
        AdvancedComponents.display_performance_monitor()
        
        st.markdown("---")
        
        # GitHub Repository Button
        st.markdown("### 🔗 Repository")
        GitHubComponents.display_github_button("https://github.com/tarunerror/debugtutor")
    
    # User profile section removed per user request
    
    # Main content
    code_input, selected_language = display_code_input()
    
    if code_input.strip():
        # Parse code if not already parsed
        if st.session_state.parsed_code is None:
            with st.spinner("Parsing code..."):
                try:
                    st.session_state.parsed_code = st.session_state.parser.parse_code(
                        code_input, selected_language
                    )
                except Exception as e:
                    st.error(f"Error parsing code: {str(e)}")
                    st.session_state.parsed_code = {}
        
        # Display parsing results
        if st.session_state.parsed_code:
            display_parsing_results(st.session_state.parsed_code)
        
        # Action buttons
        explain_error, suggest_fix, analyze_code, optimize_code = display_action_buttons(code_input, selected_language)
        
        # Process button clicks with enhanced error handling
        if explain_error and config_manager.is_valid():
            track_user_action("explain_error", selected_language)
            
            st.session_state.conversation_history.append({
                'role': 'user',
                'content': 'Please explain the error in my code'
            })
            
            # Create placeholder for streaming response
            response_placeholder = st.empty()
            full_response = ""
            
            try:
                start_time = time.time()
                with st.spinner("🔍 Analyzing error..."):
                    for chunk in st.session_state.llm_processor.explain_error_stream(
                        code_input, selected_language, st.session_state.parsed_code
                    ):
                        full_response += chunk
                        response_placeholder.markdown(f"**DebugTutor:** {full_response}▊")
                
                # Final update without cursor
                response_placeholder.markdown(f"**DebugTutor:** {full_response}")
                
                st.session_state.conversation_history.append({
                    'role': 'assistant',
                    'content': full_response
                })
                
                # Log performance
                duration = time.time() - start_time
                app_logger.log_performance("explain_error", duration)
                
                st.rerun()
                
            except Exception as e:
                app_logger.log_error(e, "explain_error")
                st.error(f"❌ Error explaining code: {str(e)}")
        
        elif suggest_fix and config_manager.is_valid():
            track_user_action("suggest_fix", selected_language)
            
            st.session_state.conversation_history.append({
                'role': 'user',
                'content': 'Please suggest a fix for my code'
            })
            
            # Create placeholder for streaming response
            response_placeholder = st.empty()
            full_response = ""
            
            try:
                start_time = time.time()
                with st.spinner("🔧 Generating fix..."):
                    for chunk in st.session_state.llm_processor.suggest_fix_stream(
                        code_input, selected_language, st.session_state.parsed_code
                    ):
                        full_response += chunk
                        response_placeholder.markdown(f"**DebugTutor:** {full_response}▊")
                
                # Final update without cursor
                response_placeholder.markdown(f"**DebugTutor:** {full_response}")
                
                st.session_state.conversation_history.append({
                    'role': 'assistant',
                    'content': full_response
                })
                
                # Track successful fix
                session_analytics.track_error_fixed()
                
                # Log performance
                duration = time.time() - start_time
                app_logger.log_performance("suggest_fix", duration)
                
                st.rerun()
                
            except Exception as e:
                app_logger.log_error(e, "suggest_fix")
                st.error(f"❌ Error suggesting fix: {str(e)}")
        
        elif analyze_code and config_manager.is_valid():
            track_user_action("analyze_code", selected_language)
            
            st.session_state.conversation_history.append({
                'role': 'user',
                'content': 'Please analyze my code'
            })
            
            # Create placeholder for streaming response
            response_placeholder = st.empty()
            full_response = ""
            
            try:
                start_time = time.time()
                with st.spinner("📊 Analyzing code..."):
                    for chunk in st.session_state.llm_processor.analyze_code_stream(
                        code_input, selected_language, st.session_state.parsed_code
                    ):
                        full_response += chunk
                        response_placeholder.markdown(f"**DebugTutor:** {full_response}▊")
                
                # Final update without cursor
                response_placeholder.markdown(f"**DebugTutor:** {full_response}")
                
                st.session_state.conversation_history.append({
                    'role': 'assistant',
                    'content': full_response
                })
                
                # Log performance
                duration = time.time() - start_time
                app_logger.log_performance("analyze_code", duration)
                
                st.rerun()
                
            except Exception as e:
                app_logger.log_error(e, "analyze_code")
                st.error(f"❌ Error analyzing code: {str(e)}")
        
        elif optimize_code and config_manager.is_valid():
            track_user_action("optimize_code", selected_language)
            
            st.session_state.conversation_history.append({
                'role': 'user',
                'content': 'Please suggest optimizations for my code'
            })
            
            # Create placeholder for streaming response
            response_placeholder = st.empty()
            full_response = ""
            
            try:
                start_time = time.time()
                with st.spinner("⚡ Optimizing code..."):
                    # Use analyze_code_stream for optimization (can be enhanced later)
                    for chunk in st.session_state.llm_processor.analyze_code_stream(
                        code_input, selected_language, st.session_state.parsed_code
                    ):
                        full_response += chunk
                        response_placeholder.markdown(f"**DebugTutor:** {full_response}▊")
                
                # Final update without cursor
                response_placeholder.markdown(f"**DebugTutor:** {full_response}")
                
                st.session_state.conversation_history.append({
                    'role': 'assistant',
                    'content': full_response
                })
                
                # Log performance
                duration = time.time() - start_time
                app_logger.log_performance("optimize_code", duration)
                
                st.rerun()
                
            except Exception as e:
                app_logger.log_error(e, "optimize_code")
                st.error(f"❌ Error optimizing code: {str(e)}")
        
        elif (explain_error or suggest_fix or analyze_code or optimize_code) and not config_manager.is_valid():
            st.warning("⚠️ Please configure your OpenRouter API key in the .env file to use AI features.")
            st.info("💡 Get your free API key from [OpenRouter](https://openrouter.ai/settings/keys)")
    
    # Display conversation and follow-up
    display_conversation()
    display_follow_up()

if __name__ == "__main__":
    try:
        # Log application start
        app_logger.log_user_action("app_start")
        main()
    except Exception as e:
        app_logger.log_error(e, "main_application")
        st.error("❌ An unexpected error occurred. Please refresh the page.")
        st.exception(e)
