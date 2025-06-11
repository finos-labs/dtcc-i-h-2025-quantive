import streamlit as st
import html
from memory.chat_memory import load_chat_history, save_chat_history
from model.llm_client import query_llm
import requests

def remove_pii(query: str) -> str:
    try:
        response = requests.post("http://localhost:5000/redact", json={"text": query})
        response.raise_for_status()
        print(response.json())
        return response.json().get("redacted_text", query)
    
    except Exception as e:
        print(f"PII remover failed: {e}")
        return query

def init_chat():
    if "chat" not in st.session_state:
        user_id = st.session_state["username"]
        st.session_state.chat = load_chat_history(user_id)

def render_chat():
    st.markdown(
        """
        <style>
        #chat-container {
            max-height: 75vh;
            overflow-y: auto;
            padding: 1rem;
            margin-bottom: 7rem;
        }
        .message-wrapper {
            display: flex;
            margin: 1.2rem 0;
        }
        .message {
            padding: 0.9rem 1.2rem;
            border-radius: 0.75rem;
            font-family: 'Segoe UI', sans-serif;
            box-shadow: 0 0 4px rgba(255, 255, 255, 0.05);
            white-space: pre-wrap;
            overflow-wrap: break-word;
            max-width: 70vw;
            line-height: 1.5;
        }
        .user-wrapper {
            justify-content: flex-end;
        }
        .user .message {
            background-color: #1f2937;
            color: #d1d5db;
            margin-right: 1rem;
        }
        .model-wrapper {
            justify-content: flex-start;
        }
        .model .message {
            background-color: #374151;
            color: #f3f4f6;
            margin-left: 1rem;
        }
        .source-links {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-top: 0.5rem;
            margin-left: 1.2rem;
        }

        .source-link {
            background-color: #4b5563;
            color: #f9fafb;
            padding: 0.4rem 0.6rem;
            border-radius: 0.5rem;
            font-size: 0.85rem;
            text-decoration: none;
        }

        .source-link:hover {
            background-color: #6b7280;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.markdown('<div id="chat-container">', unsafe_allow_html=True)
    for msg in st.session_state.chat:
        role = msg["role"]
        content = html.escape(msg["content"])
        wrapper_class = "user-wrapper user" if role == "user" else "model-wrapper model"
        st.markdown(
            f"""
            <div class="message-wrapper {wrapper_class}">
                <div class="message">{content}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

         # Display source links if available
        source_links = msg.get("source_links", [])
        if source_links:
            links_html = ''.join(
                f'<a class="source-link" href="{html.escape(link)}" target="_blank">Source {i+1}</a>'
                for i, link in enumerate(source_links)
            )
            st.markdown(f'<div class="source-links">{links_html}</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

def build_chat_history_list(chat_pairs):
    history_list = []
    for i in range(0, len(chat_pairs) - 1, 2):
        user_msg = chat_pairs[i]["content"]
        ai_msg = chat_pairs[i + 1]["content"] if i + 1 < len(chat_pairs) else ""
        history_list.append({"user": user_msg, "ai": ai_msg})
    return history_list

def chat_input_box():
    if "loading" not in st.session_state:
        st.session_state.loading = False

    apply_pii_removal = st.sidebar.checkbox("Enable PII Removal", value=True)

    st.markdown('<div class="chat-input-box">', unsafe_allow_html=True)
    with st.form("chat_form", clear_on_submit=True):
        user_query = st.text_area(
            label="Chat Input",
            placeholder="Type your message...",
            key="chat_input",
            height=100,
            label_visibility="collapsed"
        )

        col1, col2 = st.columns([18, 1])
        with col2:
            submitted = st.form_submit_button("📤")
    st.markdown('</div>', unsafe_allow_html=True)

    user_id = st.session_state.get("username", "default_user")

    if submitted and user_query.strip() and not st.session_state.loading:
        if apply_pii_removal:
            user_query = remove_pii(user_query)
        
        st.session_state.chat.append({"role": "user", "content": user_query})
        st.session_state.chat.append({"role": "model", "content": "Generating..."})
        save_chat_history(user_id, st.session_state.chat)

        st.session_state.loading = True
        st.session_state.current_query = user_query
        st.rerun()

    if st.session_state.loading:
        history_text = build_chat_history_list(st.session_state.chat[:-1])
        assistant_response, source_links = query_llm(history_text, st.session_state.current_query)

        st.session_state.chat.pop()
        st.session_state.chat.append({"role": "model", "content": assistant_response, "source_links": source_links})
        save_chat_history(user_id, st.session_state.chat)

        st.session_state.loading = False
        st.rerun()
