import streamlit as st

from chat_logic import build_system_prompt, load_portfolio, stream_answer
from jd_matcher import analyze_jd, extract_text, looks_like_jd, summarize_for_history

st.set_page_config(page_title="Askfolio · Sandeep Yadav", page_icon="💬")

LINK_ORDER = [
    ("resume", "Resume"),
    ("github", "GitHub"),
    ("linkedin", "LinkedIn"),
    ("leetcode", "LeetCode"),
    ("codolio", "Codolio"),
]

EXAMPLE_QUESTIONS = [
    "What has Sandeep built with LLMs?",
    "Which projects use Python and Pandas?",
    "Does he have Kubernetes experience?",
]


@st.cache_data
def get_portfolio():
    return load_portfolio()


try:
    portfolio = get_portfolio()
except FileNotFoundError:
    st.error("portfolio.json not found. Make sure it sits next to app.py.")
    st.stop()

system_prompt = build_system_prompt(portfolio)

if "messages" not in st.session_state:
    st.session_state.messages = []


# ---------- Rendering ----------

def score_color(score: int) -> str:
    if score >= 85:
        return "#109E6E"
    if score >= 60:
        return "#D89B12"
    return "#E2603B"


def render_match(report: dict):
    st.markdown(f"**JD fit check: {report['role_title']}**")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            f"<span style='font-size:2.3rem;font-weight:700;color:{score_color(report['fit_score'])}'>"
            f"{report['fit_score']}</span> <span style='opacity:0.6'>/ 100</span>",
            unsafe_allow_html=True,
        )
        st.caption("Fit score, the model's overall judgment")
    with col2:
        st.markdown(
            f"<span style='font-size:2.3rem;font-weight:700'>{report['covered']}</span>"
            f" <span style='opacity:0.6'>of {report['total']}</span>",
            unsafe_allow_html=True,
        )
        st.caption("Requirements backed by a project, internship, or listed skill")

    if report["removed_claims"]:
        st.caption(
            f"Evidence check moved {len(report['removed_claims'])} claimed match(es) to missing "
            f"because nothing in the portfolio backs them: {', '.join(report['removed_claims'])}"
        )

    st.markdown("**Matched**")
    if report["matched"]:
        for m in report["matched"]:
            st.markdown(f"- {m['skill']}")
            st.caption(f"  Evidence: {', '.join(m['evidence'])}")
    else:
        st.markdown("Nothing in the portfolio matches this role's requirements.")

    st.markdown("**Missing**")
    if report["missing"]:
        st.markdown("\n".join(f"- {s}" for s in report["missing"]))
    else:
        st.markdown("No major gaps found.")

    st.markdown("**Verdict**")
    st.markdown(report["verdict"])


def render_message(msg: dict):
    with st.chat_message(msg["role"]):
        if msg.get("kind") == "match":
            render_match(msg["report"])
        else:
            st.markdown(msg.get("display", msg["content"]))


def api_history():
    return [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]


# ---------- Actions ----------

def run_chat(text: str):
    st.session_state.messages.append({"role": "user", "content": text})
    render_message(st.session_state.messages[-1])

    with st.chat_message("assistant"):
        try:
            reply = st.write_stream(stream_answer(api_history(), system_prompt))
        except Exception as e:
            reply = None
            st.error(f"Something went wrong talking to the model: {e}")

    if reply:
        st.session_state.messages.append({"role": "assistant", "content": reply})


def run_match(jd_text: str, display: str):
    preview = jd_text[:300].replace("\n", " ")
    st.session_state.messages.append({
        "role": "user",
        "content": f"[Recruiter shared a job description for a fit check. Start of JD: {preview}...]",
        "display": display,
    })
    render_message(st.session_state.messages[-1])

    with st.chat_message("assistant"):
        try:
            with st.spinner("Checking the job description against the portfolio..."):
                report = analyze_jd(jd_text, portfolio).model_dump()
        except Exception as e:
            st.error(f"Fit check failed: {e}")
            return
        render_match(report)

    st.session_state.messages.append({
        "role": "assistant",
        "kind": "match",
        "report": report,
        "content": summarize_for_history(report),
    })


def handle_input(typed: str, files):
    if files:
        texts, names = [], []
        for f in files:
            try:
                texts.append(extract_text(f))
                names.append(f.name)
            except ValueError as e:
                st.error(str(e))
        if texts:
            jd_text = "\n\n".join(texts)
            if typed:
                jd_text = f"Recruiter note: {typed}\n\n{jd_text}"
            display = f"📎 {', '.join(names)}" + (f"\n\n{typed}" if typed else "")
            run_match(jd_text, display)
        elif typed:
            run_chat(typed)
        return

    if not typed:
        return
    if looks_like_jd(typed):
        display = f"📋 Pasted job description\n\n{typed[:250]}..."
        run_match(typed, display)
    else:
        run_chat(typed)


# ---------- Sidebar ----------

with st.sidebar:
    st.markdown(f"### {portfolio['name']}")
    edu = portfolio["education"][0]
    st.caption(f"{edu['degree']} · {edu['institution'].split(',')[0]} · {edu['duration'][-4:]}")

    links = portfolio.get("links", {})
    for key, label in LINK_ORDER:
        if links.get(key):
            st.markdown(f"[{label}]({links[key]})")

    st.write("")
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()


# ---------- Main ----------

st.title("Askfolio")
st.caption("Ask about Sandeep's background, or paste or attach a job description for a fit check.")

for msg in st.session_state.messages:
    render_message(msg)

pending = None
if not st.session_state.messages:
    cols = st.columns(len(EXAMPLE_QUESTIONS))
    for col, q in zip(cols, EXAMPLE_QUESTIONS):
        if col.button(q, key=q, use_container_width=True):
            pending = q

user_input = st.chat_input(
    "Ask a question, or paste / attach a job description",
    accept_file="multiple",
    file_type=["pdf", "docx"],
)

if pending:
    run_chat(pending)
elif user_input:
    typed = (user_input.text or "").strip()
    files = user_input.files or []
    handle_input(typed, files)