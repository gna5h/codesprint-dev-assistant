from typing import Optional
from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# 1. CONTEXT SCHEMA — the types of context the assistant considers
# ---------------------------------------------------------------------------
# Using Pydantic here (not a plain dict) so the shape of "context" is
# validated and self-documenting, and so it's reusable later for Task 4
# (structured outputs) without redefining anything.
class DeveloperContext(BaseModel):
    """Structured context for a single assistant request."""
 
    task_goal: str = Field(
        ..., description="What the developer is trying to accomplish right now."
    )
    developer_role: str = Field(
        ...,
        description="Seniority/role of the developer making the request, "
        "e.g. 'junior backend developer', 'senior frontend engineer'.",
    )
    constraints: list[str] = Field(
        default_factory=list,
        description="Explicit boundaries the assistant must respect, "
        "e.g. 'explanation only, no refactor suggestions'.",
    )
    relevant_code: Optional[str] = Field(
        default=None,
        description="Code snippet or file content directly relevant to the request.",
    )
    project_conventions: Optional[str] = Field(
        default=None,
        description="Team/project standards, e.g. language, framework, "
        "style guide, naming conventions.",
    )

    # ---------------------------------------------------------------------------
# 2. DYNAMIC CONTEXT INJECTION
# ---------------------------------------------------------------------------
# This is the function that fills prompts/persona_prompts.py's
# `{context_block}` slot. It is called fresh on every request with whatever
# context is actually available — nothing here is baked into the prompt.
def build_context_block(context: DeveloperContext) -> str:
    """Format a DeveloperContext into the string injected into the prompt."""
    lines = [
        f"Task goal: {context.task_goal}",
        f"Developer role: {context.developer_role}",
    ]
 
    if context.constraints:
        constraint_list = "; ".join(context.constraints)
        lines.append(f"Constraints: {constraint_list}")
 
    if context.project_conventions:
        lines.append(f"Project conventions: {context.project_conventions}")
 
    if context.relevant_code:
        lines.append(f"Relevant code:\n{context.relevant_code}")
 
    return "\n".join(lines)