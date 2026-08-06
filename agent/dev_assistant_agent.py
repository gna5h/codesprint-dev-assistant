from langchain.agents import create_react_agent, AgentExecutor
from langchain_core.prompts import PromptTemplate

from config.settings import llm
from context.context_builder import DeveloperContext, build_context_block
from prompts.persona_prompts import SENIOR_DEV_ASSISTANT_PERSONA
from tools.code_analysis_tool import analyze_code
from tools.task_summary_tool import summarize_task

# ---------------------------------------------------------------------------
# TOOLS REGISTRY
# ---------------------------------------------------------------------------
TOOLS = [analyze_code, summarize_task]

# ---------------------------------------------------------------------------
# REACT PROMPT TEMPLATE
# ---------------------------------------------------------------------------
# create_react_agent requires exactly these four variables to be present:
#   {tools}            — rendered tool descriptions  (auto-filled by the agent)
#   {tool_names}       — comma-separated names       (auto-filled by the agent)
#   {input}            — the user's question         (provided at invocation)
#   {agent_scratchpad} — running Thought/Obs record  (managed by AgentExecutor)
#
# {persona} and {context_block} are pre-filled via .partial() so each agent
# instance already has the right persona and developer context baked in before
# the first token is generated.
#
# HOW THE AGENT CHOOSES: reason vs. tool
# ----------------------------------------
# The DECISION RULE section of the prompt gives the LLM an explicit policy:
#   - Answer directly   → if the question can be answered from training
#                         knowledge plus the supplied context.
#   - Call analyze_code → if the question requires knowing what is *inside*
#                         a code snippet the agent has not yet inspected.
#   - Call summarize_task → if the task description is too long or ambiguous
#                           to reason about cleanly without distilling it first.
#
# The ReAct loop (Reason → Act → Observe) gives the LLM a structured way to
# express that decision: it writes a Thought explaining its reasoning, then
# either names a tool (Action) or skips straight to Final Answer.
# AgentExecutor parses each turn's output, calls the named tool, injects the
# Observation, and repeats until the LLM produces "Final Answer:".
_REACT_TEMPLATE = """{persona}

CONTEXT:
{context_block}

---
TOOLS AVAILABLE:
{tools}

DECISION RULE — choose the right path for each turn:
- Answer directly (Final Answer) if you can respond accurately from the context
  and your training knowledge alone.
- Call analyze_code if the question requires inspecting a code snippet you have
  not yet examined.
- Call summarize_task if the task description is too long or ambiguous to reason
  about clearly without distilling it first.

Use this exact format every turn:

Question: the input question you must answer
Thought: decide whether to answer directly or call a tool, and explain why
Action: the tool to call, must be one of [{tool_names}]
Action Input: the exact input to pass to that tool
Observation: the result returned by the tool
... (Thought / Action / Action Input / Observation may repeat as needed)
Thought: I now have everything I need to give a final answer
Final Answer: the final, structured response following the output style in the persona

Begin!

Question: {input}
Thought:{agent_scratchpad}"""


# ---------------------------------------------------------------------------
# AGENT FACTORY
# ---------------------------------------------------------------------------
def build_agent(context: DeveloperContext) -> AgentExecutor:
    """Return a ready-to-invoke AgentExecutor configured for the given context.

    Args:
        context: A validated DeveloperContext describing the current task,
                 developer role, constraints, and optional code / conventions.

    Returns:
        AgentExecutor that exposes a .invoke({"input": "..."}) interface.
    """
    context_block = build_context_block(context)

    prompt = PromptTemplate.from_template(_REACT_TEMPLATE).partial(
        persona=SENIOR_DEV_ASSISTANT_PERSONA,
        context_block=context_block,
    )

    agent = create_react_agent(llm=llm, tools=TOOLS, prompt=prompt)

    return AgentExecutor(
        agent=agent,
        tools=TOOLS,
        verbose=True,       # prints Thought/Action/Observation for inspection
        max_iterations=6,   # prevents infinite loops on parsing failures
        handle_parsing_errors=True,
    )
