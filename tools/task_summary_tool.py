import re
from langchain_core.tools import tool


@tool
def summarize_task(task_description: str) -> str:
    """Distil a verbose or mixed-concern task description into its core goal,
    concrete sub-tasks, and explicit constraints.

    Use this tool when the input is long, ambiguous, or blends multiple
    concerns — distilling it first produces a cleaner basis for planning
    or code generation.
    Do NOT use it when the task description is already short and clear.
    """
    text = task_description.strip()
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]

    main_goal = sentences[0] if sentences else text[:120]

    action_re = re.compile(
        r'\b(create|build|implement|add|fix|update|refactor|write|design|'
        r'test|validate|generate|return|expose|integrate)\b',
        re.I,
    )
    sub_tasks = [s for s in sentences[1:] if action_re.search(s)][:5]

    constraint_re = re.compile(
        r'\b(must|should not|cannot|only|never|always|ensure|avoid|limit|'
        r'no more than|do not|don\'t)\b',
        re.I,
    )
    constraints = [s for s in sentences if constraint_re.search(s)][:3]

    parts = [f"Goal: {main_goal}"]
    if sub_tasks:
        parts.append("Sub-tasks:\n" + "\n".join(f"  - {t}" for t in sub_tasks))
    if constraints:
        parts.append("Constraints:\n" + "\n".join(f"  - {c}" for c in constraints))

    return "\n".join(parts)
