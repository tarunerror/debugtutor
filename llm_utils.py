import requests
import json
from typing import Dict, List, Any, Optional, Generator
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class LLMProcessor:
    """LLM processor using OpenRouter API with LangChain-style prompt orchestration"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENROUTER_API_KEY')
        self.base_url = os.getenv('OPENROUTER_BASE_URL', "https://openrouter.ai/api/v1/chat/completions")
        self.model = os.getenv('OPENROUTER_MODEL', "deepseek/deepseek-r1-distill-llama-70b:free")
        self.headers = {
            "Content-Type": "application/json"
        }
        
        # Set authorization header if API key is available
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"
        
        # Prompt templates
        self.error_analysis_prompt = """You are DebugTutor, an expert programming tutor that helps students debug code.

TASK: Analyze the following code and explain any errors in simple, educational terms.

CODE LANGUAGE: {language}
CODE:
```{language}
{code}
```

SYNTAX ANALYSIS RESULTS:
{syntax_analysis}

Please provide:
1. **Error Identification**: What specific errors exist?
2. **Simple Explanation**: Explain each error in beginner-friendly terms
3. **Why It Happens**: Common reasons this error occurs
4. **Learning Tips**: How to avoid this error in the future

Be encouraging and educational. Act like a patient tutor, not just a code analyzer."""

        self.fix_suggestion_prompt = """You are DebugTutor, an expert programming tutor that helps students fix their code.

TASK: Provide a corrected version of the code with detailed explanations.

CODE LANGUAGE: {language}
CODE:
```{language}
{code}
```

SYNTAX ANALYSIS RESULTS:
{syntax_analysis}

Please provide:
1. **Corrected Code**: The fixed version with proper formatting
2. **Step-by-Step Explanation**: Explain each change you made
3. **Reasoning**: Why each change fixes the issue
4. **Best Practices**: Additional improvements for better code quality

Format the corrected code in a code block and explain your reasoning clearly."""

        self.code_analysis_prompt = """You are DebugTutor, an expert programming tutor that analyzes code quality.

TASK: Analyze the following code for potential improvements and best practices.

CODE LANGUAGE: {language}
CODE:
```{language}
{code}
```

SYNTAX ANALYSIS RESULTS:
{syntax_analysis}

Please provide:
1. **Code Quality Assessment**: Overall quality and structure
2. **Potential Issues**: Any logic errors, inefficiencies, or bad practices
3. **Improvement Suggestions**: Specific recommendations
4. **Best Practices**: How to make the code more maintainable and readable

Be constructive and educational in your feedback."""

        self.follow_up_prompt = """You are DebugTutor, continuing a conversation about debugging code.

CONVERSATION HISTORY:
{conversation_history}

CURRENT CODE:
```{language}
{code}
```

USER QUESTION: {question}

Please answer the user's question in the context of the ongoing conversation. Be helpful, educational, and encouraging. Reference the code and previous discussion as needed."""

    def set_api_key(self, api_key: str):
        """Set the OpenRouter API key (deprecated - use environment variables instead)"""
        self.api_key = api_key
        self.headers["Authorization"] = f"Bearer {api_key}"
    
    def _make_api_request(self, messages: List[Dict[str, str]], max_retries: int = 3, stream: bool = False) -> str:
        """Make API request to OpenRouter with retry logic"""
        if not self.api_key:
            raise ValueError("OpenRouter API key not found. Please set OPENROUTER_API_KEY in your .env file.")
        
        payload = {
            "model": self.model,
            "messages": messages,
            "max_tokens": 2000,
            "temperature": 0.7,
            "top_p": 0.9,
            "stream": stream
        }
        
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=30,
                    stream=stream
                )
                
                if response.status_code == 200:
                    if stream:
                        return response  # Return the response object for streaming
                    else:
                        result = response.json()
                        if 'choices' in result and len(result['choices']) > 0:
                            return result['choices'][0]['message']['content']
                        else:
                            raise ValueError("Invalid response format from API")
                
                elif response.status_code == 429:  # Rate limit
                    if attempt < max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                        continue
                    else:
                        raise ValueError("Rate limit exceeded. Please try again later.")
                
                else:
                    error_msg = f"API request failed with status {response.status_code}"
                    try:
                        error_detail = response.json().get('error', {}).get('message', '')
                        if error_detail:
                            error_msg += f": {error_detail}"
                    except:
                        pass
                    raise ValueError(error_msg)
                    
            except requests.exceptions.Timeout:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    raise ValueError("Request timeout. Please check your internet connection.")
            
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    continue
                else:
                    raise ValueError(f"Network error: {str(e)}")
        
        raise ValueError("Failed to get response after multiple retries")
    
    def _format_syntax_analysis(self, parsed_result: Dict[str, Any]) -> str:
        """Format syntax analysis results for prompt"""
        if not parsed_result:
            return "No syntax analysis available."
        
        result = []
        
        if parsed_result.get('syntax_errors'):
            result.append("SYNTAX ERRORS:")
            for error in parsed_result['syntax_errors']:
                line = error.get('line', 'Unknown')
                message = error.get('message', 'Unknown error')
                result.append(f"- Line {line}: {message}")
        else:
            result.append("SYNTAX ERRORS: None detected")
        
        if parsed_result.get('warnings'):
            result.append("\nWARNINGS:")
            for warning in parsed_result['warnings']:
                line = warning.get('line', 'Unknown')
                message = warning.get('message', 'Unknown warning')
                result.append(f"- Line {line}: {message}")
        else:
            result.append("\nWARNINGS: None detected")
        
        return "\n".join(result)
    
    def explain_error(self, code: str, language: str, parsed_result: Dict[str, Any]) -> str:
        """Explain errors in the code"""
        syntax_analysis = self._format_syntax_analysis(parsed_result)
        
        prompt = self.error_analysis_prompt.format(
            language=language,
            code=code,
            syntax_analysis=syntax_analysis
        )
        
        messages = [
            {"role": "system", "content": "You are DebugTutor, an expert programming tutor focused on helping students learn through debugging."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_api_request(messages)
    
    def suggest_fix(self, code: str, language: str, parsed_result: Dict[str, Any]) -> str:
        """Suggest fixes for the code"""
        syntax_analysis = self._format_syntax_analysis(parsed_result)
        
        prompt = self.fix_suggestion_prompt.format(
            language=language,
            code=code,
            syntax_analysis=syntax_analysis
        )
        
        messages = [
            {"role": "system", "content": "You are DebugTutor, an expert programming tutor who provides clear, corrected code with educational explanations."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_api_request(messages)
    
    def analyze_code(self, code: str, language: str, parsed_result: Dict[str, Any]) -> str:
        """Analyze code quality and provide suggestions"""
        syntax_analysis = self._format_syntax_analysis(parsed_result)
        
        prompt = self.code_analysis_prompt.format(
            language=language,
            code=code,
            syntax_analysis=syntax_analysis
        )
        
        messages = [
            {"role": "system", "content": "You are DebugTutor, an expert programming tutor who analyzes code quality and provides constructive feedback."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_api_request(messages)
    
    def process_follow_up(self, question: str, code: str, conversation_history: List[Dict[str, str]]) -> str:
        """Process follow-up questions in context"""
        # Format conversation history
        history_text = ""
        for msg in conversation_history[-6:]:  # Last 6 messages for context
            role = "User" if msg['role'] == 'user' else "DebugTutor"
            history_text += f"{role}: {msg['content']}\n\n"
        
        prompt = self.follow_up_prompt.format(
            conversation_history=history_text,
            language="python",  # Default, could be improved to detect language
            code=code,
            question=question
        )
        
        messages = [
            {"role": "system", "content": "You are DebugTutor, continuing an educational conversation about debugging code."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_api_request(messages)
    
    def get_step_by_step_explanation(self, code: str, language: str, specific_error: str) -> str:
        """Get detailed step-by-step explanation for a specific error"""
        prompt = f"""You are DebugTutor. Provide a detailed, step-by-step explanation for debugging this specific error.

CODE LANGUAGE: {language}
CODE:
```{language}
{code}
```

SPECIFIC ERROR: {specific_error}

Please provide:
1. **Step 1**: Identify the exact location of the error
2. **Step 2**: Understand what the code is trying to do
3. **Step 3**: Explain why the error occurs
4. **Step 4**: Show how to fix it
5. **Step 5**: Verify the fix works
6. **Step 6**: Prevent similar errors in the future

Make each step clear and educational, as if teaching a beginner."""

        messages = [
            {"role": "system", "content": "You are DebugTutor, providing step-by-step debugging guidance."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_api_request(messages)
    
    def explain_concept(self, concept: str, language: str, code_context: str = "") -> str:
        """Explain a programming concept in the context of the code"""
        prompt = f"""You are DebugTutor. Explain the programming concept "{concept}" in simple terms.

PROGRAMMING LANGUAGE: {language}

CODE CONTEXT (if relevant):
```{language}
{code_context}
```

Please provide:
1. **Simple Definition**: What is {concept}?
2. **Why It Matters**: Why is this concept important?
3. **Common Examples**: Show simple examples
4. **In This Context**: How it relates to the user's code (if applicable)
5. **Common Mistakes**: What beginners often get wrong

Keep the explanation beginner-friendly and encouraging."""

        messages = [
            {"role": "system", "content": "You are DebugTutor, explaining programming concepts in an educational way."},
            {"role": "user", "content": prompt}
        ]
        
        return self._make_api_request(messages)
    
    def _make_streaming_request(self, messages: List[Dict[str, str]]) -> Generator[str, None, None]:
        """Make streaming API request to OpenRouter"""
        response = self._make_api_request(messages, stream=True)
        
        try:
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        data = line[6:]  # Remove 'data: ' prefix
                        if data == '[DONE]':
                            break
                        try:
                            json_data = json.loads(data)
                            if 'choices' in json_data and len(json_data['choices']) > 0:
                                delta = json_data['choices'][0].get('delta', {})
                                if 'content' in delta:
                                    yield delta['content']
                        except json.JSONDecodeError:
                            continue
        finally:
            response.close()
    
    def explain_error_stream(self, code: str, language: str, parsed_result: Dict[str, Any]) -> Generator[str, None, None]:
        """Explain errors in the code with streaming response"""
        syntax_analysis = self._format_syntax_analysis(parsed_result)
        
        prompt = self.error_analysis_prompt.format(
            language=language,
            code=code,
            syntax_analysis=syntax_analysis
        )
        
        messages = [
            {"role": "system", "content": "You are DebugTutor, an expert programming tutor focused on helping students learn through debugging."},
            {"role": "user", "content": prompt}
        ]
        
        yield from self._make_streaming_request(messages)
    
    def suggest_fix_stream(self, code: str, language: str, parsed_result: Dict[str, Any]) -> Generator[str, None, None]:
        """Suggest fixes for the code with streaming response"""
        syntax_analysis = self._format_syntax_analysis(parsed_result)
        
        prompt = self.fix_suggestion_prompt.format(
            language=language,
            code=code,
            syntax_analysis=syntax_analysis
        )
        
        messages = [
            {"role": "system", "content": "You are DebugTutor, an expert programming tutor who provides clear, corrected code with educational explanations."},
            {"role": "user", "content": prompt}
        ]
        
        yield from self._make_streaming_request(messages)
    
    def analyze_code_stream(self, code: str, language: str, parsed_result: Dict[str, Any]) -> Generator[str, None, None]:
        """Analyze code quality and provide suggestions with streaming response"""
        syntax_analysis = self._format_syntax_analysis(parsed_result)
        
        prompt = self.code_analysis_prompt.format(
            language=language,
            code=code,
            syntax_analysis=syntax_analysis
        )
        
        messages = [
            {"role": "system", "content": "You are DebugTutor, an expert programming tutor who analyzes code quality and provides constructive feedback."},
            {"role": "user", "content": prompt}
        ]
        
        yield from self._make_streaming_request(messages)
    
    def process_follow_up_stream(self, question: str, code: str, conversation_history: List[Dict[str, str]]) -> Generator[str, None, None]:
        """Process follow-up questions in context with streaming response"""
        # Format conversation history
        history_text = ""
        for msg in conversation_history[-6:]:  # Last 6 messages for context
            role = "User" if msg['role'] == 'user' else "DebugTutor"
            history_text += f"{role}: {msg['content']}\n\n"
        
        prompt = self.follow_up_prompt.format(
            conversation_history=history_text,
            language="python",  # Default, could be improved to detect language
            code=code,
            question=question
        )
        
        messages = [
            {"role": "system", "content": "You are DebugTutor, continuing an educational conversation about debugging code."},
            {"role": "user", "content": prompt}
        ]
        
        yield from self._make_streaming_request(messages)
