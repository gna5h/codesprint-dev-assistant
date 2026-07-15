# CodeSprint Dev Assistant

**Sage** — an agent-driven AI assistant that helps developers at CodeSprint
Studio move faster through the routine, repetitive parts of software work:
understanding unfamiliar code, planning small features, debugging, and
generating boilerplate.

CodeSprint Studio is a software consultancy that helps startups rapidly
build and maintain web applications. As projects grow, developers spend an
increasing share of their time on tasks that are individually small but
collectively expensive — re-reading legacy code to understand it, writing
one-off prompts to an LLM and getting inconsistent results back, manually
chaining together "understand → reason → generate → validate" steps, and
copy-pasting outputs between tools because nothing returns a predictable
format.

Sage is built to remove that overhead. It combines:

- **A consistent persona and prompting layer**, so output tone and structure
  don't vary from one ad-hoc prompt to the next.
- **Context-aware reasoning**, so the assistant's answers reflect the actual
  task, developer role, and constraints at hand — not a generic response.
- **An agent that decides for itself** when to simply answer and when it
  needs to call a tool (e.g. to analyze code or summarize a task) to get a
  reliable answer.
- **Structured, validated output**, so results can be consumed directly by
  other systems instead of needing to be re-parsed from free text.
- **An orchestrated multi-step workflow**, so the full
  reason → act → validate cycle happens automatically, with clear points
  where a human can review before anything downstream depends on it.

The result is an assistant that behaves the same way every time it's asked
to do the same kind of task, and that developers can trust to hand off small
work to, rather than one more chat window to babysit.

---

## How It Works

At a high level, a request flows through Sage like this:

1. **Prompt layer** — the request is wrapped in a fixed persona and
   instruction template, so tone and output shape stay consistent.
2. **Context layer** — relevant context (task goal, developer role,
   constraints, relevant code) is gathered and injected into the prompt
   dynamically, rather than being baked into the template itself.
3. **Agent layer** — the agent reasons about the request and decides whether
   it can answer directly or needs to invoke a tool (e.g. to inspect code or
   pull metadata) before responding.
4. **Output layer** — the final response is returned as a validated,
   schema-conformant object (not raw text), so it's safe to pass to other
   systems.
5. **Workflow layer** — all of the above is chained together end-to-end,
   with defined points where a human can step in and review before the
   result is used further.

---

## Project Structure

```
codesprint-dev-assistant/
├── config/       # Model config, environment loading
├── prompts/      # Persona and prompt templates
├── context/      # Dynamic context-gathering and injection logic
├── tools/        # Tool functions the agent can call (code analysis, summarization, etc.)
├── agent/        # Agent setup — reasoning vs. tool-use decision logic
├── schemas/      # Structured output schemas and validation
├── workflow/     # End-to-end orchestration chaining every layer together
├── examples/     # Sample input/output runs
├── diagrams/     # Architecture / workflow diagrams
├── requirements.txt
└── README.md
```

---

## Tech Stack

- **LangChain v1.0** — orchestration framework
- **Gemini** (via `langchain-google-genai`) — underlying LLM
- **Pydantic** — structured output validation
- **python-dotenv** — environment/config management

---

## Setup

```bash
# 1. Create and activate a virtual environment
python -m venv env1
source env1/bin/activate        # macOS/Linux
# env1\Scripts\Activate.ps1     # Windows PowerShell

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your Gemini API key
cp .env.example .env
# then edit .env and set GEMINI_API_KEY=your_key_here
```