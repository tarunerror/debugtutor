# 🐛 DebugTutor - AI Code Debugging Assistant

**DebugTutor** is a Progressive Web App (PWA) that helps users debug code interactively using AI. It combines code parsing with Tree-sitter, AI-powered analysis using OpenRouter's DeepSeek model, and a modern Streamlit interface to provide step-by-step debugging guidance like a human tutor.

## ✨ Features

- **🔐 Google Authentication**: Secure sign-in with Google OAuth via Supabase
- **👤 User Profiles**: Display user information (name, email, avatar) after login
- **🔍 Smart Code Analysis**: Uses Tree-sitter for syntax parsing and error detection
- **🤖 AI-Powered Debugging**: Leverages OpenRouter's DeepSeek model for intelligent error explanations
- **💬 Interactive Tutoring**: Conversational interface for follow-up questions
- **🌐 Multi-Language Support**: Python, JavaScript, TypeScript, C++, Java, Go, Rust
- **📱 Progressive Web App**: Installable, works offline, modern UI
- **🎯 Educational Focus**: Explains errors in beginner-friendly terms with learning tips

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- OpenRouter API key (free tier available)
- Supabase account (for Google authentication)

### Installation

1. **Clone or download the project**:
   ```bash
   cd debugger
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**:
   - Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```
   - Edit the `.env` file with your actual values:
   ```bash
   # OpenRouter API (for AI features)
   OPENROUTER_API_KEY=your_openrouter_api_key_here
   
   # Supabase (for Google authentication)
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_ANON_KEY=your_supabase_anon_key_here
   REDIRECT_URL=http://localhost:8501
   ```
   - Get your OpenRouter API key from [OpenRouter](https://openrouter.ai/settings/keys)
   - Create a Supabase project at [Supabase](https://supabase.com) and enable Google OAuth

4. **Run the application**:
   ```bash
   streamlit run main.py
   ```

5. **Open your browser**:
   - Navigate to `http://localhost:8501`
   - The API key will be loaded automatically from your `.env` file
   - Start debugging code!

## 🎯 How to Use

### Basic Debugging Workflow

1. **Select Language**: Choose your programming language from the dropdown
2. **Paste Code**: Enter your buggy code in the text area
3. **Analyze**: The app automatically parses your code for syntax errors
4. **Get Help**: Click one of the action buttons:
   - **🔍 Explain Error**: Get detailed error explanations
   - **🔧 Suggest Fix**: Get corrected code with explanations
   - **📊 Analyze Code**: Get code quality feedback

### Interactive Learning

- **Ask Follow-up Questions**: Use the conversation panel to ask specific questions
- **Step-by-Step Guidance**: Get detailed explanations for each error
- **Learn Best Practices**: Receive tips to avoid similar errors in the future

### Example Session

```python
# Paste this buggy Python code:
def calculate_average(numbers)
    total = 0
    for num in numbers:
        total += num
    return total / len(numbers)

result = calculate_average([1, 2, 3, 4, 5])
print("Average:", result
```

The app will:
1. Detect the missing colon and parenthesis
2. Explain why these errors occur
3. Provide the corrected code
4. Offer tips to prevent similar mistakes

## 🏗️ Architecture

### Core Components

- **`main.py`**: Streamlit UI and main application logic
- **`parser.py`**: Code parsing using Tree-sitter and AST analysis
- **`llm_utils.py`**: OpenRouter API integration with educational prompts
- **`pwa_config/`**: Progressive Web App configuration files

### Technology Stack

- **Frontend**: Streamlit with custom CSS
- **Code Parsing**: Tree-sitter + Python AST
- **AI Model**: OpenRouter DeepSeek R1 (free tier)
- **PWA**: Service Worker + Web App Manifest

## 🌐 PWA Features

### Installation
- Click the install button in your browser
- Add to home screen on mobile devices
- Works like a native app

### Offline Support
- Caches the UI for offline use
- Stores your last session
- Shows offline indicators when needed

### Mobile Optimized
- Responsive design
- Touch-friendly interface
- Works on all devices

## 🔧 Configuration

### Environment Variables (Required)

The application now uses environment variables for configuration. Edit the `.env` file:

```env
OPENROUTER_API_KEY=your_api_key_here
OPENROUTER_MODEL=deepseek/deepseek-r1-distill-llama-70b:free
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1/chat/completions
```

**Important**: The API key is no longer entered through the UI for security reasons.

### Customizing the AI Model

Edit `llm_utils.py` to change the model:

```python
self.model = "deepseek/deepseek-r1-distill-llama-70b:free"  # Free model
# or
self.model = "openai/gpt-4"  # Paid model (better quality)
```

## 🎨 Customization

### Adding New Languages

1. **Update `parser.py`**:
   ```python
   self.supported_languages['your_language'] = self._parse_your_language
   ```

2. **Implement parsing logic**:
   ```python
   def _parse_your_language(self, code: str) -> Dict[str, Any]:
       # Your parsing logic here
       pass
   ```

3. **Update the UI**:
   ```python
   languages = ["python", "javascript", "your_language", ...]
   ```

### Customizing Prompts

Edit the prompt templates in `llm_utils.py`:

```python
self.error_analysis_prompt = """
Your custom prompt here...
"""
```

## 🐛 Troubleshooting

### Common Issues

**"API key not found" error**:
- Make sure you've set `OPENROUTER_API_KEY` in your `.env` file
- Check that the key is valid and has credits
- Restart the application after updating the `.env` file

**"Parser error" messages**:
- This usually means the code has severe syntax issues
- Try fixing obvious syntax errors first

**Slow responses**:
- Free tier models may have rate limits
- Consider upgrading to a paid model for faster responses

**PWA not installing**:
- Make sure you're using HTTPS (required for PWA)
- Check that your browser supports PWA installation

### Getting Help

1. **Check the conversation history** for previous explanations
2. **Ask follow-up questions** using the chat interface
3. **Try different languages** if parsing fails
4. **Simplify your code** for better analysis

## 🔒 Privacy & Security

- **No Code Storage**: Your code is only sent to OpenRouter for analysis
- **API Key Security**: Keys are stored in environment variables (not in the UI)
- **No Tracking**: The app doesn't collect or store personal data

## 🚀 Deployment

### Local Development
```bash
streamlit run main.py --server.port 8501
```

### Production Deployment

**Using Streamlit Cloud**:
1. Push code to GitHub
2. Connect to Streamlit Cloud
3. Deploy with one click

**Using Docker**:
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "main.py"]
```

## 🤝 Contributing

We welcome contributions! Here's how to help:

1. **Report Bugs**: Use GitHub issues for bug reports
2. **Suggest Features**: Propose new features or improvements
3. **Add Languages**: Implement support for new programming languages
4. **Improve Prompts**: Enhance the AI prompts for better responses

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **OpenRouter** for providing free AI model access
- **Streamlit** for the excellent web framework
- **Tree-sitter** for robust code parsing
- **DeepSeek** for the powerful language model

---

## 🎓 Educational Use

DebugTutor is designed as an educational tool. It's perfect for:

- **Students** learning to program
- **Educators** teaching debugging skills
- **Developers** getting quick explanations for unfamiliar errors
- **Code Review** sessions and pair programming

The AI tutor approach helps users understand not just *what* is wrong, but *why* it's wrong and *how* to fix it, promoting better learning outcomes than simple error correction.

---

**Happy Debugging! 🐛➡️✨**
