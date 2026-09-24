import streamlit as st

from chat_logic import build_system_prompt, load_portfolio, stream_answer

st.set_page_config(page_title="Askfolio", page_icon="💬")

st.title("Askfolio")
st.caption("Ask anything about Sandeep Yadav's background, skills, and projects.")


@st.cache_data
def get_system_prompt():
    portfolio = load_portfolio()
    return build_system_prompt(portfolio)


try:
    system_prompt = get_system_prompt()
except FileNotFoundError:
    st.error("portfolio.json not found. Make sure it sits next to app.py.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

prompt = st.chat_input("What would you like to know?")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            reply = st.write_stream(stream_answer(st.session_state.messages, system_prompt))
        except Exception as e:
            reply = None
            st.error(f"Something went wrong talking to the model: {e}")

    if reply:
        st.session_state.messages.append({"role": "assistant", "content": reply})