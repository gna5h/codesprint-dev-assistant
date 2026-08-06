"""
schemas/output_schemas.py — Step 4: Structured Outputs and Validation

Why structured outputs improve reliability and integration
----------------------------------------------------------
1. **Type safety** — callers receive `response.summary` (a validated `str`),
   not `output["summary"]` (a dict key that may be absent or the wrong type).
   Pydantic raises `ValidationError` immediately if a required field is missing
   or ill-typed, surfacing contract violations at the boundary rather than
   silently propagating bad data downstream.

2. **Predictable downstream contracts** — APIs, UI components, and test suites
   can depend on the schema definition rather than fragile regex/text-parsing
   logic.  A breaking change to the schema is a compile-time (import-time)
   error, not a runtime surprise.

3. **Self-documenting for the LLM** — `Field(description=...)` annotations are
   read by `llm.with_structured_output()` and injected into the function-calling
   spec sent to the model, which improves output quality without any extra
   prompt engineering.
"""

from __future__ import annotations

from typing import Literal

from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# 1. AssistantResponse — mirrors the four-section CODE_EXPLANATION_PROMPT
# ---------------------------------------------------------------------------

class AssistantResponse(BaseModel):
    """Validated output for a single developer-assistant response."""

    summary: str = Field(
        ...,
        description="One or two sentences describing what the code or requirement does.",
    )
    breakdown: list[str] = Field(
        ...,
        description="Numbered steps walking through the logic or requirement in order.",
    )
    key_considerations: list[str] = Field(
        ...,
        description="Edge cases, assumptions, or risks the developer should be aware of.",
    )
    next_steps: list[str] = Field(
        ...,
        description="Concrete actions the developer should take after reading this response.",
    )
    confidence: Literal["high", "medium", "low"] = Field(
        ...,
        description=(
            "Agent's self-reported certainty: 'high' when all relevant context is "
            "available, 'medium' when some assumptions were made, 'low' when the "
            "question is ambiguous or context is missing."
        ),
    )


# ---------------------------------------------------------------------------
# 2. RiskItem + RiskAssessment — for task-level risk evaluation
# ---------------------------------------------------------------------------

class RiskItem(BaseModel):
    """A single identified risk within a task or codebase change."""

    description: str = Field(
        ...,
        description="A short, specific description of the risk.",
    )
    severity: Literal["critical", "high", "medium", "low"] = Field(
        ...,
        description="How serious this risk is if it materialises.",
    )
    mitigation: str = Field(
        ...,
        description="Concrete action to reduce or eliminate this risk.",
    )


class RiskAssessment(BaseModel):
    """Aggregate risk evaluation for a task or set of changes."""

    overall_risk: Literal["critical", "high", "medium", "low"] = Field(
        ...,
        description="The highest-severity risk level present, used as the headline rating.",
    )
    risks: list[RiskItem] = Field(
        default_factory=list,
        description="All individual risks identified, ordered from most to least severe.",
    )
    recommendation: str = Field(
        ...,
        description="One or two sentences summarising what the team should do next.",
    )


# ---------------------------------------------------------------------------
# 3. response_parser — PydanticOutputParser for text → AssistantResponse
# ---------------------------------------------------------------------------
# Usage:
#   instructions = response_parser.get_format_instructions()  # inject into prompt
#   result: AssistantResponse = response_parser.parse(raw_text)

response_parser: PydanticOutputParser = PydanticOutputParser(
    pydantic_object=AssistantResponse
)


# ---------------------------------------------------------------------------
# 4. get_structured_response() — primary validation via with_structured_output
# ---------------------------------------------------------------------------

def get_structured_response(raw_output: str) -> AssistantResponse:
    """Parse and validate a raw agent Final Answer into an AssistantResponse.

    Uses `llm.with_structured_output()` (Gemini's native function-calling path)
    so the model actively conforms its reply to the schema rather than requiring
    post-hoc text extraction.

    The LLM import is deferred to this function so that importing this module
    does not require a GEMINI_API_KEY — only calling this function does.

    Args:
        raw_output: The string returned in the agent's "Final Answer:" field.

    Returns:
        A validated AssistantResponse instance.

    Raises:
        ValidationError: If the structured output does not satisfy the schema.
    """
    from config.settings import llm  # deferred: avoids API key requirement at import time

    structured_llm = llm.with_structured_output(AssistantResponse)
    prompt = (
        "Convert the following developer assistant response into the required "
        "structured format.  Preserve all information; do not add or omit content.\n\n"
        f"{raw_output}"
    )
    return structured_llm.invoke(prompt)


# ---------------------------------------------------------------------------
# 5. EXAMPLE_RESPONSE — hardcoded validated instance
# ---------------------------------------------------------------------------
# Shows exactly what a correctly-structured AssistantResponse looks like.
# Useful for tests, documentation, and prompt examples.

EXAMPLE_RESPONSE = AssistantResponse(
    summary=(
        "This function iterates over a list of database records and applies a "
        "discount calculation before writing results back to the store."
    ),
    breakdown=[
        "1. Accepts a list of `Order` objects and a float `discount_rate`.",
        "2. Validates that `discount_rate` is between 0.0 and 1.0; raises "
        "`ValueError` otherwise.",
        "3. Loops through each order and multiplies `order.total` by "
        "`(1 - discount_rate)`.",
        "4. Persists the updated orders via `order_repo.save_batch(orders)`.",
        "5. Returns the count of successfully updated records.",
    ],
    key_considerations=[
        "Floating-point multiplication can introduce rounding errors on currency "
        "values — consider using `decimal.Decimal` instead of `float`.",
        "`save_batch` is not wrapped in a transaction; a partial failure would "
        "leave the dataset in an inconsistent state.",
        "No logging or audit trail is written when discounts are applied.",
    ],
    next_steps=[
        "Switch `discount_rate` and `order.total` to `Decimal` to avoid "
        "currency rounding issues.",
        "Wrap `save_batch` in a database transaction so the update is atomic.",
        "Add a structured log entry (order ID, old total, new total) for auditing.",
    ],
    confidence="high",
)
