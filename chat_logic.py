import json
import os
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

PORTFOLIO_PATH = Path(__file__).parent / "portfolio.json"

MAX_TOKENS = 700
MAX_HISTORY_MESSAGES = 12


def load_portfolio(path=PORTFOLIO_PATH):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_system_prompt(portfolio):
    data = json.dumps(portfolio, indent=2, ensure_ascii=False)
    return f"""You are a portfolio assistant for Sandeep Yadav. Recruiters and hiring managers talk to you to learn about him.

Answer ONLY from the portfolio data below. This is a hard rule.

Rules you must follow:
1. If something is not in the portfolio data, say you do not have that information. Do not guess, do not estimate, do not infer.
2. Never claim a skill, tool, framework, company, or year of experience that is not written in the data.
3. If asked about anything listed under "not_yet_available", state plainly that Sandeep has not worked with it.
4. Do not convert a project mention into professional work experience. Projects are projects, internships are internships.
5. If asked to compare Sandeep to an ideal candidate or a job description, only use what is in the data. Missing skills should be reported as missing, not softened.
6. Keep answers short and factual. Two to four sentences for most questions.
7. Speak about Sandeep in third person. Stay professional, no hype words.

Portfolio data:
{data}
"""


def get_client():
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not found. Check your .env file or Streamlit secrets.")
    return Groq(api_key=api_key)


def get_model():
    return os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")


def trim_history(messages):
    if len(messages) <= MAX_HISTORY_MESSAGES:
        return messages
    return messages[-MAX_HISTORY_MESSAGES:]


def stream_answer(history, system_prompt):
    client = get_client()
    payload = [{"role": "system", "content": system_prompt}] + trim_history(history)

    stream = client.chat.completions.create(
        model=get_model(),
        messages=payload,
        max_tokens=MAX_TOKENS,
        temperature=0.2,
        stream=True,
    )

    for chunk in stream:
        piece = chunk.choices[0].delta.content
        if piece:
            yield piece