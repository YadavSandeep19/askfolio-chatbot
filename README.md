# Askfolio

A chat interface where recruiters can ask questions about Sandeep Yadav's background, skills, and projects, and get answers grounded strictly in his portfolio data.

**Live demo:** _(link added after deploy)_

Hosted on Streamlit Community Cloud free tier. The app sleeps after 12 hours of inactivity, so the first load can take around 30 seconds.

## What it does

- Answers questions about education, skills, internships, and projects from a single portfolio data file
- Refuses to answer anything not present in that data instead of guessing
- Streams responses token by token

## Stack

Python, Streamlit, Groq LLM API, python-dotenv

## Running locally

1. Clone the repo and create a virtual environment
2. `pip install -r requirements.txt`
3. Create a `.env` file with `GROQ_API_KEY` and `GROQ_MODEL`
4. `streamlit run app.py`

## Project structure

- `app.py` — Streamlit UI
- `chat_logic.py` — portfolio loading, system prompt, Groq calls
- `portfolio.json` — all portfolio content, editable without touching code