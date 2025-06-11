def init_session():
    import streamlit as st
    if "username" not in st.session_state:
        st.session_state["username"] = None

def is_logged_in():
    import streamlit as st
    return st.session_state.get("username") is not None

def login_user(username):
    import streamlit as st
    st.session_state["username"] = username

def logout_user():
    import streamlit as st
    st.session_state["username"] = None
    st.session_state["email"] = None

