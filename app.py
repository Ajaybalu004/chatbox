import streamlit as st
from chatbox_v7 import get_response

st.set_page_config(page_title="Chatbox AI", page_icon="🤖")

st.title("🤖 Chatbox AI")
st.caption("Ask me anything — in any language.")

# Keep chat history across reruns
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display past messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Chat input box
user_input = st.chat_input("Type your message...")

if user_input:
    # Show user message
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # Get bot response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = get_response(user_input)
        st.write(response)
    st.session_state.messages.append({"role": "assistant", "content": response})