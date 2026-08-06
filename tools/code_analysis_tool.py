import re
from langchain_core.tools import tool


@tool
def analyze_code(code: str) -> str:
    """Inspect a code snippet and return a structured report: detected language,
    functions and classes defined, imports present, and any obvious code-quality
    issues (bare excepts, hardcoded credentials).

    Use this tool when the user's question requires knowing *what is in* a
    code snippet before you can reason about it or explain it accurately.
    Do NOT use it for conversational questions that don't involve inspecting code.
    """
    lines = code.strip().splitlines()
    non_empty = [ln for ln in lines if ln.strip()]

    # Language detection (heuristic — not exhaustive)
    if re.search(r'\bdef \w+\s*\(|^\s*(?:import|from) \w+', code, re.M):
        language = "Python"
    elif re.search(r'function\s+\w+\s*\(|(?:const|let|var)\s+\w+\s*=|=>\s*[\{\(]', code):
        language = "JavaScript / TypeScript"
    elif re.search(r'public\s+class |System\.out\.print|void\s+main\s*\(', code):
        language = "Java"
    else:
        language = "Unrecognised"

    functions = re.findall(r'\bdef (\w+)\s*\(', code)
    classes   = re.findall(r'\bclass (\w+)', code)
    imports   = re.findall(r'^(?:import|from)\s+(\S+)', code, re.M)

    issues = []
    if re.search(r'\bexcept\s*:', code):
        issues.append("bare 'except:' clause (hides errors)")
    if re.search(r'(?i)(?:password|secret|api_key)\s*=\s*["\']', code):
        issues.append("possible hardcoded credential")
    if not issues:
        issues.append("none detected by static scan")

    return (
        f"Language  : {language}\n"
        f"Lines     : {len(lines)} total, {len(non_empty)} non-empty\n"
        f"Functions : {', '.join(functions) or 'none'}\n"
        f"Classes   : {', '.join(classes) or 'none'}\n"
        f"Imports   : {', '.join(imports) or 'none'}\n"
        f"Issues    : {'; '.join(issues)}"
    )
