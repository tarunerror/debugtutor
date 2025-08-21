import re
from typing import Dict, List, Any, Optional
import ast
import json

class CodeParser:
    """Code parser that analyzes syntax and detects potential errors"""
    
    def __init__(self):
        self.supported_languages = {
            'python': self._parse_python,
            'javascript': self._parse_javascript,
            'typescript': self._parse_javascript,  # Similar parsing logic
            'cpp': self._parse_cpp,
            'java': self._parse_java,
            'go': self._parse_go,
            'rust': self._parse_rust
        }
    
    def parse_code(self, code: str, language: str) -> Dict[str, Any]:
        """
        Parse code and return analysis results
        
        Args:
            code: Source code to parse
            language: Programming language
            
        Returns:
            Dictionary containing parsing results, errors, and warnings
        """
        if not code.strip():
            return {
                'syntax_errors': [],
                'warnings': [],
                'ast': None,
                'language': language,
                'line_count': 0
            }
        
        language = language.lower()
        
        if language not in self.supported_languages:
            return {
                'syntax_errors': [{'line': 1, 'message': f'Unsupported language: {language}'}],
                'warnings': [],
                'ast': None,
                'language': language,
                'line_count': len(code.split('\n'))
            }
        
        try:
            return self.supported_languages[language](code)
        except Exception as e:
            return {
                'syntax_errors': [{'line': 1, 'message': f'Parser error: {str(e)}'}],
                'warnings': [],
                'ast': None,
                'language': language,
                'line_count': len(code.split('\n'))
            }
    
    def _parse_python(self, code: str) -> Dict[str, Any]:
        """Parse Python code using AST"""
        syntax_errors = []
        warnings = []
        ast_tree = None
        
        try:
            # Try to parse with AST
            ast_tree = ast.parse(code)
            
            # Check for common Python issues
            warnings.extend(self._check_python_warnings(code, ast_tree))
            
        except SyntaxError as e:
            syntax_errors.append({
                'line': e.lineno or 1,
                'column': e.offset or 1,
                'message': e.msg or 'Syntax error',
                'type': 'SyntaxError'
            })
        except Exception as e:
            syntax_errors.append({
                'line': 1,
                'message': f'Parse error: {str(e)}',
                'type': 'ParseError'
            })
        
        return {
            'syntax_errors': syntax_errors,
            'warnings': warnings,
            'ast': ast_tree,
            'language': 'python',
            'line_count': len(code.split('\n'))
        }
    
    def _check_python_warnings(self, code: str, ast_tree: ast.AST) -> List[Dict[str, Any]]:
        """Check for common Python warnings and potential issues"""
        warnings = []
        lines = code.split('\n')
        
        # Check for common issues
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Unused imports (basic check)
            if line_stripped.startswith('import ') or line_stripped.startswith('from '):
                module_name = self._extract_import_name(line_stripped)
                if module_name and not self._is_module_used(code, module_name):
                    warnings.append({
                        'line': i,
                        'message': f'Potentially unused import: {module_name}',
                        'type': 'UnusedImport'
                    })
            
            # Missing parentheses in print (Python 2 style)
            if re.search(r'\bprint\s+[^(]', line_stripped):
                warnings.append({
                    'line': i,
                    'message': 'Consider using print() with parentheses',
                    'type': 'PrintStatement'
                })
            
            # Undefined variables (basic check)
            if '=' in line_stripped and not line_stripped.startswith('#'):
                undefined_vars = self._check_undefined_variables(line_stripped, code)
                for var in undefined_vars:
                    warnings.append({
                        'line': i,
                        'message': f'Potentially undefined variable: {var}',
                        'type': 'UndefinedVariable'
                    })
        
        return warnings
    
    def _parse_javascript(self, code: str) -> Dict[str, Any]:
        """Parse JavaScript/TypeScript code with basic syntax checking"""
        syntax_errors = []
        warnings = []
        lines = code.split('\n')
        
        # Basic syntax checks
        brace_count = 0
        paren_count = 0
        bracket_count = 0
        in_string = False
        string_char = None
        
        for i, line in enumerate(lines, 1):
            for j, char in enumerate(line):
                if not in_string:
                    if char in ['"', "'", '`']:
                        in_string = True
                        string_char = char
                    elif char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                    elif char == '(':
                        paren_count += 1
                    elif char == ')':
                        paren_count -= 1
                    elif char == '[':
                        bracket_count += 1
                    elif char == ']':
                        bracket_count -= 1
                else:
                    if char == string_char and (j == 0 or line[j-1] != '\\'):
                        in_string = False
                        string_char = None
            
            # Check for common JavaScript issues
            line_stripped = line.strip()
            
            # Missing semicolons
            if (line_stripped and 
                not line_stripped.endswith((';', '{', '}', ')', ',')) and
                not line_stripped.startswith(('if', 'for', 'while', 'function', 'class', '//', '/*')) and
                '=' in line_stripped):
                warnings.append({
                    'line': i,
                    'message': 'Consider adding semicolon at end of statement',
                    'type': 'MissingSemicolon'
                })
            
            # Undefined variables (basic check)
            if 'console.log' in line_stripped:
                # This is fine, just an example check
                pass
        
        # Check for unmatched brackets
        if brace_count != 0:
            syntax_errors.append({
                'line': len(lines),
                'message': f'Unmatched braces: {brace_count} extra {"opening" if brace_count > 0 else "closing"}',
                'type': 'UnmatchedBraces'
            })
        
        if paren_count != 0:
            syntax_errors.append({
                'line': len(lines),
                'message': f'Unmatched parentheses: {paren_count} extra {"opening" if paren_count > 0 else "closing"}',
                'type': 'UnmatchedParentheses'
            })
        
        if bracket_count != 0:
            syntax_errors.append({
                'line': len(lines),
                'message': f'Unmatched brackets: {bracket_count} extra {"opening" if bracket_count > 0 else "closing"}',
                'type': 'UnmatchedBrackets'
            })
        
        return {
            'syntax_errors': syntax_errors,
            'warnings': warnings,
            'ast': None,
            'language': 'javascript',
            'line_count': len(lines)
        }
    
    def _parse_cpp(self, code: str) -> Dict[str, Any]:
        """Parse C++ code with basic syntax checking"""
        syntax_errors = []
        warnings = []
        lines = code.split('\n')
        
        # Basic C++ checks
        has_main = False
        includes = []
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for main function
            if 'int main' in line_stripped or 'void main' in line_stripped:
                has_main = True
            
            # Check for includes
            if line_stripped.startswith('#include'):
                includes.append(line_stripped)
            
            # Check for missing semicolons
            if (line_stripped and 
                not line_stripped.endswith((';', '{', '}', ':', '#')) and
                not line_stripped.startswith(('if', 'for', 'while', 'class', '//', '/*', '#')) and
                '=' in line_stripped):
                warnings.append({
                    'line': i,
                    'message': 'Possible missing semicolon',
                    'type': 'MissingSemicolon'
                })
        
        if not has_main and len(lines) > 5:  # Only warn for substantial code
            warnings.append({
                'line': 1,
                'message': 'No main function found',
                'type': 'NoMainFunction'
            })
        
        return {
            'syntax_errors': syntax_errors,
            'warnings': warnings,
            'ast': None,
            'language': 'cpp',
            'line_count': len(lines),
            'includes': includes
        }
    
    def _parse_java(self, code: str) -> Dict[str, Any]:
        """Parse Java code with basic syntax checking"""
        syntax_errors = []
        warnings = []
        lines = code.split('\n')
        
        has_main = False
        has_class = False
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for main method
            if 'public static void main' in line_stripped:
                has_main = True
            
            # Check for class declaration
            if line_stripped.startswith('public class') or line_stripped.startswith('class'):
                has_class = True
            
            # Check for missing semicolons
            if (line_stripped and 
                not line_stripped.endswith((';', '{', '}', ')', ':')) and
                not line_stripped.startswith(('if', 'for', 'while', 'public', 'private', 'class', '//', '/*')) and
                ('=' in line_stripped or 'return' in line_stripped)):
                warnings.append({
                    'line': i,
                    'message': 'Possible missing semicolon',
                    'type': 'MissingSemicolon'
                })
        
        if not has_class and len(lines) > 3:
            warnings.append({
                'line': 1,
                'message': 'No class declaration found',
                'type': 'NoClass'
            })
        
        return {
            'syntax_errors': syntax_errors,
            'warnings': warnings,
            'ast': None,
            'language': 'java',
            'line_count': len(lines)
        }
    
    def _parse_go(self, code: str) -> Dict[str, Any]:
        """Parse Go code with basic syntax checking"""
        syntax_errors = []
        warnings = []
        lines = code.split('\n')
        
        has_package = False
        has_main = False
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for package declaration
            if line_stripped.startswith('package '):
                has_package = True
            
            # Check for main function
            if 'func main()' in line_stripped:
                has_main = True
        
        if not has_package:
            syntax_errors.append({
                'line': 1,
                'message': 'Missing package declaration',
                'type': 'MissingPackage'
            })
        
        return {
            'syntax_errors': syntax_errors,
            'warnings': warnings,
            'ast': None,
            'language': 'go',
            'line_count': len(lines)
        }
    
    def _parse_rust(self, code: str) -> Dict[str, Any]:
        """Parse Rust code with basic syntax checking"""
        syntax_errors = []
        warnings = []
        lines = code.split('\n')
        
        has_main = False
        
        for i, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            # Check for main function
            if 'fn main()' in line_stripped:
                has_main = True
        
        return {
            'syntax_errors': syntax_errors,
            'warnings': warnings,
            'ast': None,
            'language': 'rust',
            'line_count': len(lines)
        }
    
    def _extract_import_name(self, import_line: str) -> Optional[str]:
        """Extract module name from import statement"""
        if import_line.startswith('import '):
            return import_line.replace('import ', '').split('.')[0].split(' as ')[0].strip()
        elif import_line.startswith('from '):
            parts = import_line.split(' ')
            if len(parts) >= 2:
                return parts[1].split('.')[0].strip()
        return None
    
    def _is_module_used(self, code: str, module_name: str) -> bool:
        """Basic check if a module is used in the code"""
        lines = code.split('\n')
        for line in lines:
            if module_name in line and not line.strip().startswith(('import ', 'from ')):
                return True
        return False
    
    def _check_undefined_variables(self, line: str, full_code: str) -> List[str]:
        """Basic check for potentially undefined variables"""
        # This is a simplified implementation
        # In a real implementation, you'd want more sophisticated analysis
        undefined_vars = []
        
        # Extract variable names from the right side of assignments
        if '=' in line:
            right_side = line.split('=', 1)[1].strip()
            # Look for variable names (simplified regex)
            vars_in_line = re.findall(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', right_side)
            
            for var in vars_in_line:
                # Skip built-in functions and keywords
                if var not in ['print', 'len', 'str', 'int', 'float', 'list', 'dict', 'True', 'False', 'None']:
                    # Check if variable is defined before this line (very basic check)
                    if f'{var} =' not in full_code.split(line)[0]:
                        undefined_vars.append(var)
        
        return undefined_vars
