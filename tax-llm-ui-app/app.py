import streamlit as st 
from auth.login import login_or_signup_form, get_user_email
from utils.session import init_session, is_logged_in, login_user, logout_user
from chat.chat_ui import init_chat, render_chat, chat_input_box
from memory.chat_memory import load_chat_history, save_chat_history
from notification.subscription import subscription_ui, get_user_subscriptions
from notification.alerts import alerts_ui

st.set_page_config(page_title="Tax LLM Chat", layout="wide")
init_session()

if not is_logged_in():
    user_id = login_or_signup_form()
    if user_id:
        login_user(user_id)
        st.rerun()
        
else:
    user_id = st.session_state["username"]
    if "email" not in st.session_state:
        st.session_state["email"] = get_user_email(user_id)

    user_email = st.session_state["email"]

    st.sidebar.write(f"Logged in as: {user_id}")

    if st.sidebar.button("Logout"):
        logout_user()
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    if st.sidebar.button("Clear Chat"):
        st.session_state.pop("chat", None)
        user_id = st.session_state["username"]
        save_chat_history(user_id, [])
        st.success("Chat history cleared.")
        st.rerun()

    st.title("Tax Insights LLM")

    tab1, tab2 = st.tabs(["Chat", "Notifications"])

    with tab1:
        init_chat()
        render_chat()
        chat_input_box()

    with tab2:
        col1, col2 = st.columns([3, 1])

        with col1:
            st.subheader("Alert Feed")
            user_subs = get_user_subscriptions(user_id)
            alerts_ui(user_id, user_subs)

        with col2:
            st.subheader("Manage Subscriptions")
            subscription_ui(user_id, user_email)