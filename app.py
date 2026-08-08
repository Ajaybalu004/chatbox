import streamlit as st
import streamlit_authenticator as stauth
import yaml
import os
from yaml.loader import SafeLoader
from database import init_db, create_conversation, get_conversations, save_message, load_messages, delete_conversation, rename_conversation
from chatbox_v7 import get_response
import smtplib
from email.mime.text import MIMEText
init_db()

# ===== NEW: create config.yaml from Streamlit secrets if it doesn't exist =====
if not os.path.exists('config.yaml'):
    config_content = f"""
credentials:
  usernames:
    ajay:
      email: ajaybalu0210@gmail.com
      name: Ajay Balu
      password: {st.secrets["ADMIN_PASSWORD_HASH"]}

cookie:
  name: chatbox_auth_cookie
  key: {st.secrets["COOKIE_KEY"]}
  expiry_days: 30
"""
    with open('config.yaml', 'w') as f:
        f.write(config_content)
# ==================================================================

with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

def send_reset_email(to_email, new_password):
    sender_email = os.getenv("EMAIL_ADDRESS")
    sender_password = os.getenv("EMAIL_APP_PASSWORD")

    msg = MIMEText(f"Your Chatbox AI password has been reset.\n\nYour new password is: {new_password}\n\nPlease log in and consider changing it.")
    msg['Subject'] = "Chatbox AI - Password Reset"
    msg['From'] = sender_email
    msg['To'] = to_email

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)

if "show_signup" not in st.session_state:
    st.session_state.show_signup = False

if st.session_state.get('authentication_status') is not True:
    if "auth_view" not in st.session_state:
        st.session_state.auth_view = "login"

    if st.session_state.auth_view == "login":
        authenticator.login(location='main')

        col1, col2 = st.columns(2)
        with col1:
            if st.button("Don't have an account? Sign up"):
                st.session_state.auth_view = "signup"
                st.rerun()
        with col2:
            if st.button("Forgot password?"):
                st.session_state.auth_view = "forgot"
                st.rerun()

    elif st.session_state.auth_view == "forgot":
        st.subheader("Forgot Password")
        try:
            username_of_forgotten_password, email_of_forgotten_password, new_random_password = authenticator.forgot_password()
            if username_of_forgotten_password:
                send_reset_email(email_of_forgotten_password, new_random_password)
                with open('config.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
                st.success("A new password has been sent to your email.")
            elif username_of_forgotten_password == False:
                st.error("Username not found.")
        except Exception as e:
            st.error(e)

        if st.button("← Back to Login"):
            st.session_state.auth_view = "login"
            st.rerun()

    elif st.session_state.auth_view == "signup":
        try:
            email, username, name = authenticator.register_user()
            if email:
                with open('config.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
                st.session_state['authentication_status'] = True
                st.session_state['username'] = username
                st.session_state['name'] = name
                st.session_state.auth_view = "login"
                st.success(f"Welcome, {name}! Logging you in...")
                st.rerun()
        except Exception as e:
            st.error(e)

        if st.button("← Back to Login"):
            st.session_state.auth_view = "login"
            st.rerun()

if st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')
    st.stop()
elif st.session_state.get('authentication_status') is None:
    st.warning('Please log in or sign up to continue')
    st.stop()

if st.session_state.get('authentication_status') is False:
    st.error('Username/password is incorrect')
    st.stop()
elif st.session_state.get('authentication_status') is None:
    st.stop()

username = st.session_state["username"]

# ===== NEW: ask if user wants to change password, once per session ======
if "password_prompt_shown" not in st.session_state:
    st.session_state.password_prompt_shown = False

if not st.session_state.password_prompt_shown:
    st.subheader("Welcome back!")
    st.write("Would you like to change your password now?")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Yes, change my password"):
            st.session_state.show_password_change = True
            st.session_state.password_prompt_shown = True
            st.rerun()
    with col2:
        if st.button("No, continue to chat"):
            st.session_state.password_prompt_shown = True
            st.rerun()
    st.stop()
if st.session_state.get("show_password_change", False):
    st.subheader("Change your password")

    if st.session_state.get("password_changed", False):
        st.success("Password changed successfully!")
        if st.button("Continue to chat"):
            st.session_state.show_password_change = False
            st.session_state.password_changed = False
            st.rerun()
    else:
        try:
            if authenticator.reset_password(username):
                with open('config.yaml', 'w') as file:
                    yaml.dump(config, file, default_flow_style=False)
                st.session_state.password_changed = True
                st.rerun()
        except Exception as e:
            st.error(e)
    st.stop()
# ==========================================================================

st.set_page_config(
    page_title="Chatbox AI",
    page_icon="🤖",
    layout="centered"
)

SYSTEM_PROMPT = {"role": "system", "content": "You are Chatbox AI, a helpful, knowledgeable assistant. Answer clearly and concisely. If you don't know something, say so honestly. Keep a friendly, professional tone."}

with st.sidebar:
    if st.session_state.get('authentication_status'):
        authenticator.logout()
    st.header("🤖 Chatbox AI")
    st.divider()

    if st.button("➕ New Chat", use_container_width=True):
        new_id = create_conversation(username)
        st.session_state.current_conversation_id = new_id
        st.session_state.message = []
        st.session_state.llm_history = [SYSTEM_PROMPT]
        st.rerun()

    st.divider()

    conversations = get_conversations(username)
    for convo in conversations:
        col1, col2 = st.columns([4, 1])
        with col1:
            if st.button(convo["title"], key=f"convo_{convo['id']}", use_container_width=True):
                st.session_state.current_conversation_id = convo["id"]
                st.session_state.message = load_messages(convo["id"])
                st.session_state.llm_history = [SYSTEM_PROMPT] + st.session_state.message
                st.rerun()
        with col2:
            if st.button("🗑️", key=f"delete_{convo['id']}"):
                delete_conversation(convo["id"])
                if st.session_state.get("current_conversation_id") == convo["id"]:
                    new_id = create_conversation(username)
                    st.session_state.current_conversation_id = new_id
                    st.session_state.message = []
                    st.session_state.llm_history = [SYSTEM_PROMPT]
                st.rerun()

st.title("🤖 Chatbox AI")
st.caption("Ask me anything — in any language.")

if "current_conversation_id" not in st.session_state:
    conversations = get_conversations(username)
    if conversations:
        st.session_state.current_conversation_id = conversations[0]["id"]
        st.session_state.message = load_messages(conversations[0]["id"])
    else:
        st.session_state.current_conversation_id = create_conversation(username)
        st.session_state.message = []

if "llm_history" not in st.session_state:
    st.session_state.llm_history = [SYSTEM_PROMPT] + st.session_state.message

example_clicked = None

for msg in st.session_state.message:
    avatar = "🧑" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.write(msg["content"])

user_input = st.chat_input("Type your message...")

final_input = user_input if user_input else example_clicked

if final_input:
    conv_id = st.session_state.current_conversation_id

    if not st.session_state.message:
        title = final_input[:40] + ("..." if len(final_input) > 40 else "")
        rename_conversation(conv_id, title)

    st.session_state.message.append({"role": "user", "content": final_input})
    save_message(conv_id, "user", final_input)
    with st.chat_message("user", avatar="🧑"):
        st.write(final_input)

    with st.chat_message("assistant", avatar="🤖"):
        with st.spinner("Thinking..."):
            response = get_response(final_input, st.session_state.llm_history)
        st.write(response)
    st.session_state.message.append({"role": "assistant", "content": response})
    save_message(conv_id, "assistant", response)
    st.rerun()

st.divider()
st.caption("⚡ Powered by Groq (Llama 3.3) · Built with Streamlit")