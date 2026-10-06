# Askfolio

A chat assistant where recruiters ask about Sandeep Yadav's background, skills, and projects, and get answers grounded only in his portfolio data. Recruiters can also paste or attach a job description to get an evidence-backed fit check.

**Live demo:** https://askfolio.streamlit.app/

Hosted on Streamlit Community Cloud free tier. The app sleeps after 12 hours of inactivity, so the first load can take around 30 seconds.

## What it does

- Answers questions about education, skills, internship, and projects from a single portfolio data file
- Refuses anything not present in that data instead of guessing
- Streams chat responses token by token
- Runs a fit check when a job description is pasted or attached as PDF or DOCX

## How the fit check stays honest

Most resume matchers ask a model for a score and print whatever comes back. Askfolio adds checks in code:

- The model must return JSON that passes a Pydantic schema. Malformed output is retried once, then rejected.
- Every matched skill must name the project or internship that proves it. The code checks those names against the portfolio, and any claimed match with no real backing is moved to missing and shown to the recruiter.
- Requirement coverage ("4 of 6 requirements backed") is counted in code, separate from the model's holistic score.
- The job description is treated as untrusted text, so instructions hidden inside it are ignored.

## Stack

Python, Streamlit, Groq LLM API, Pydantic, pypdf, python-docx, python-dotenv

## Running locally

1. Clone the repo and create a virtual environment
2. `pip install -r requirements.txt`
3. Create a `.env` file with `GROQ_API_KEY` and `GROQ_MODEL`
4. `streamlit run app.py`

## Project structure

- `app.py`: Streamlit UI only
- `chat_logic.py`: portfolio loading, chat system prompt, streaming Groq calls
- `jd_matcher.py`: JD file reading, Pydantic schemas, fit check and evidence verification
- `portfolio.json`: all portfolio content and links, editable without touching code
