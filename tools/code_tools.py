"""
tools/code_tools.py
Code analysis tools: AST parsing, pylint, complexity analysis.
"""
import ast
import subprocess
import tempfile
import os
from langchain_core.tools import tool


@tool
def analyze_python_syntax(code: str) -> str:
    """
    Parse Python code and check for syntax errors using AST.
    Returns a structured report of the code's syntax tree summary.
    """
    try:
        tree = ast.parse(code)
        functions = [n.name for n in ast.walk(tree) if isinstance(n, ast.FunctionDef)]
        classes = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        imports = [
            ast.unparse(n) for n in ast.walk(tree)
            if isinstance(n, (ast.Import, ast.ImportFrom))
        ]
        lines = code.strip().split("\n")
        return (
            f"✅ Syntax: Valid Python\n"
            f"📏 Lines: {len(lines)}\n"
            f"🔧 Functions: {functions or ['none']}\n"
            f"🏛️  Classes: {classes or ['none']}\n"
            f"📦 Imports: {imports or ['none']}"
        )
    except SyntaxError as e:
        return f"❌ Syntax Error: {e.msg} at line {e.lineno}\n  → {e.text}"


@tool
def run_pylint(code: str) -> str:
    """
    Run pylint on the given Python code and return linting issues.
    Checks for errors, warnings, and code style violations.
    """
    with tempfile.NamedTemporaryFile(suffix=".py", mode="w", delete=False) as f:
        f.write(code)
        tmp_path = f.name
    try:
        result = subprocess.run(
            ["pylint", tmp_path, "--output-format=text", "--score=yes",
             "--disable=C0114,C0115,C0116"],  # suppress missing docstring warnings
            capture_output=True, text=True, timeout=30
        )
        output = result.stdout + result.stderr
        # Clean up temp file path from output for cleaner display
        output = output.replace(tmp_path, "<code>")
        return output if output.strip() else "✅ No pylint issues found."
    except FileNotFoundError:
        return "⚠️  pylint not installed. Run: pip install pylint"
    except subprocess.TimeoutExpired:
        return "⏱️  pylint timed out."
    finally:
        os.unlink(tmp_path)


@tool
def calculate_complexity(code: str) -> str:
    """
    Calculate cyclomatic complexity of Python functions.
    Returns complexity score and recommendation.
    """
    try:
        import radon.complexity as rc
        results = rc.cc_visit(code)
        if not results:
            return "ℹ️  No functions/classes found to analyze."
        lines = ["📊 Cyclomatic Complexity Report:", ""]
        for block in sorted(results, key=lambda b: b.complexity, reverse=True):
            rating = "A" if block.complexity <= 5 else "B" if block.complexity <= 10 else "C" if block.complexity <= 15 else "D"
            emoji = "✅" if rating in ("A", "B") else "⚠️" if rating == "C" else "❌"
            lines.append(f"  {emoji} {block.name} (line {block.lineno}): complexity={block.complexity} [{rating}]")
        return "\n".join(lines)
    except ImportError:
        return "⚠️  radon not installed. Run: pip install radon"
    except Exception as e:
        return f"⚠️  Complexity analysis failed: {e}"


@tool
def check_security_issues(code: str) -> str:
    """
    Scan Python code for common security vulnerabilities.
    Checks for hardcoded secrets, dangerous functions, SQL injection risks, etc.
    """
    issues = []
    lines = code.split("\n")

    danger_patterns = {
        "eval(": "🔴 HIGH: Use of eval() — arbitrary code execution risk",
        "exec(": "🔴 HIGH: Use of exec() — arbitrary code execution risk",
        "pickle.loads": "🔴 HIGH: pickle.loads() — deserialization attack risk",
        "subprocess.shell=True": "🟡 MEDIUM: shell=True in subprocess — command injection risk",
        "os.system(": "🟡 MEDIUM: os.system() — prefer subprocess with shell=False",
        "password =": "🟠 MEDIUM: Possible hardcoded password",
        "secret =": "🟠 MEDIUM: Possible hardcoded secret",
        "api_key =": "🟠 MEDIUM: Possible hardcoded API key",
        "MD5": "🟡 LOW: MD5 is cryptographically weak, use SHA-256+",
        "SHA1": "🟡 LOW: SHA1 is cryptographically weak, use SHA-256+",
        "random.random": "🟡 LOW: random is not cryptographically secure, use secrets module",
    }

    for lineno, line in enumerate(lines, 1):
        for pattern, message in danger_patterns.items():
            if pattern.lower() in line.lower():
                issues.append(f"  Line {lineno}: {message}")

    if not issues:
        return "✅ No obvious security issues detected."
    return "🔒 Security Scan Results:\n" + "\n".join(issues)
