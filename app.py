import streamlit as st
from chatbox_v7 import get_response

st.set_page_config(page_title="Aura AI", page_icon="🤖")

st.title("🤖 Aura AI")
st.caption("Ask me anything — in any language.")

# Chat display history (what's shown on screen)
if "message" not in st.session_state:
    st.session_state.message = []

# LLM conversation memory (what the model actually sees)
if "llm_history" not in st.session_state:
    st.session_state.llm_history = [
        {"role": "system", "content": "You are Aura AI, a helpful, knowledgeable assistant. Answer clearly and concisely. If you don't know something, say so honestly. Keep a friendly, professional tone."}
    ]

for msg in st.session_state.message:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

user_input = st.chat_input("Type your message...")

if user_input:
    st.session_state.message.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_response(user_input, st.session_state.llm_history)
        st.write(response)
    st.session_state.message.append({"role": "assistant", "content": response})