import sys
import os
from pathlib import Path

# Add the parent directory to the Python path
parent_dir = Path(__file__).parent.parent
sys.path.insert(0, str(parent_dir))

# Set environment variables for Streamlit
os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
os.environ['STREAMLIT_SERVER_PORT'] = '8501'
os.environ['STREAMLIT_SERVER_ENABLE_CORS'] = 'false'
os.environ['STREAMLIT_BROWSER_GATHER_USAGE_STATS'] = 'false'

from streamlit.web import cli as stcli
from streamlit import config as st_config

def handler(request):
    """Vercel handler for Streamlit app"""
    # Configure Streamlit for serverless
    st_config.set_option('server.headless', True)
    st_config.set_option('server.port', 8501)
    st_config.set_option('server.enableCORS', False)
    st_config.set_option('browser.gatherUsageStats', False)
    
    # Run the main app
    sys.argv = ['streamlit', 'run', str(parent_dir / 'main.py')]
    stcli.main()
    
    return {
        'statusCode': 200,
        'body': 'DebugTutor is running'
    }
