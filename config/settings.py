import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# ---------------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------------
# temperature=0 keeps outputs deterministic — important for a developer tool
# where consistency and reliability are explicit project requirements.
llm = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    google_api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0,
)
