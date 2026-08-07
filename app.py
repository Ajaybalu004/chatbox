import streamlit as st
from chatbox_v7 import get_response

st.set_page_config(
    page_title="Chatbox AI",
    page_icon="🤖",
    layout="centered"
)

with st.sidebar:
    st.header("🤖 Chatbox AI")
    st.divider()
    if st.button("🗑️ Clear chat"):
        st.session_state.message = []
        st.session_state.llm_history = [
            {"role": "system", "content": "You are Chatbox AI, a helpful, knowledgeable assistant. Answer clearly and concisely. If you don't know something, say so honestly. Keep a friendly, professional tone."}
        ]
        st.rerun()

st.title("🤖 Chatbox AI")
st.caption("Ask me anything — in any language.")

if "message" not in st.session_state:
    st.session_state.message = []

if "llm_history" not in st.session_state:
    st.session_state.llm_history = [
        {"role": "system", "content": "You are Chatbox AI, a helpful, knowledgeable assistant. Answer clearly and concisely. If you don't know something, say so honestly. Keep a friendly, professional tone."}
    ]

# ===== NEW: Welcome message + example prompts (only shown before first message) =====
if not st.session_state.message:
    st.info("👋 Try asking me something — in any language!")
    col1, col2, col3 = st.columns(3)
    example_clicked = None
    with col1:
        if st.button("Explain gravity"):
            example_clicked = "Explain gravity in simple terms"
    with col2:
        if st.button("Tell me a joke"):
            example_clicked = "Tell me a joke"
    with col3:
        if st.button("नमस्ते"):
            example_clicked = "नमस्ते"
else:
    example_clicked = None
# =======================================================================

for msg in st.session_state.message:
    avatar = "🧑" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

user_input = st.chat_input("Type your message...")

# ===== NEW: use example button click if no typed input =====
final_input = user_input if user_input else example_clicked
# ==============================================================

if final_input:
    st.session_state.message.append({"role": "user", "content": final_input})
    with st.chat_message("user", avatar="🧑"):
        st.write(final_input)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            response = get_response(final_input, st.session_state.llm_history)
        st.write(response)
    st.session_state.message.append({"role": "assistant", "content": response})
    st.rerun()

st.divider()
st.caption("⚡ Powered by Groq (Llama 3.3) · Built with Streamlit")