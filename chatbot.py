import streamlit as st
import google.generativeai as genai
import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration
DATA_DIR = Path("chat_data")
DATA_DIR.mkdir(exist_ok=True)
DATA_FILE = DATA_DIR / "chat_history.json"

# Initialize Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    st.error("❌ Missing GEMINI_API_KEY in .env")
    st.stop()
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


def generate_chat_id():
    return str(int(time.time() * 1000))

def load_chats():
    if DATA_FILE.exists():
        try:
            with open(DATA_FILE, "r") as f:
                chats = json.load(f)
                for chat_id in chats:
                    if "created_at" not in chats[chat_id]:
                        chats[chat_id]["created_at"] = chat_id if chat_id.isdigit() else str(int(time.time() * 1000))
                return chats
        except Exception as e:
            st.error(f"Error loading chat history: {e}")
            return {}
    return {}

def save_chats():
    try:
        with open(DATA_FILE, "w") as f:
            json.dump(st.session_state.all_chats, f, indent=2)
    except Exception as e:
        st.error(f"Error saving chat history: {e}")

# Initialize session state
if "all_chats" not in st.session_state:
    st.session_state.all_chats = load_chats()
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None

# Handle URL params
url_chat_id = st.query_params.get("chat_id", None)
if url_chat_id and url_chat_id in st.session_state.all_chats:
    st.session_state.current_chat_id = url_chat_id

# Sidebar - Chat List
with st.sidebar:
    st.header("Chat History")
    
    # New Chat Button
    if st.button("＋ New Chat", key="new_chat", use_container_width=True):
        new_id = generate_chat_id()
        st.session_state.all_chats[new_id] = {
            "title": "New Chat",
            "messages": [],
            "created_at": new_id
        }
        st.session_state.current_chat_id = new_id
        st.query_params["chat_id"] = new_id
        save_chats()
        st.rerun()
    
    st.divider()
    
    if not st.session_state.all_chats:
        st.markdown('<div class="empty-state">No conversations yet</div>', unsafe_allow_html=True)
    else:
        for chat_id in sorted(
            st.session_state.all_chats.keys(),
            key=lambda x: int(st.session_state.all_chats[x].get("created_at", 0)),
            reverse=True
        ):
            chat = st.session_state.all_chats[chat_id]
            is_active = chat_id == st.session_state.current_chat_id
            
            created_time = time.strftime('%b %d %H:%M', time.localtime(int(chat.get("created_at", 0))/1000))
            
            btn = st.button(
                f"💬 {chat['title']}",
                key=f"chat_btn_{chat_id}",
                help=f"Created: {created_time}",
                type="secondary" if is_active else "tertiary"
            )
            
            if btn:
                st.session_state.current_chat_id = chat_id
                st.query_params["chat_id"] = chat_id
                st.rerun()

# Main Chat Area
if st.session_state.current_chat_id:
    current_chat = st.session_state.all_chats[st.session_state.current_chat_id]
    st.title("💬 Gemini Chat")
    
    for msg in current_chat["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    if prompt := st.chat_input("Type your message..."):
        if not current_chat["messages"] and prompt.strip():
            current_chat["title"] = prompt[:20] + ("..." if len(prompt) > 20 else "")
        
        current_chat["messages"].append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = model.generate_content(prompt)
                    current_chat["messages"].append({"role": "assistant", "content": response.text})
                    st.markdown(response.text)
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    current_chat["messages"].append({"role": "assistant", "content": error_msg})
                    st.error(error_msg)
        
        st.query_params["chat_id"] = st.session_state.current_chat_id
        save_chats()
        st.rerun()
else:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
        <div class="empty-state">
            <h3>Welcome to Gemini Chat</h3>
            <p>Start a new conversation to begin</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Start Chatting", key="start_chat", use_container_width=True):
            new_id = generate_chat_id()
            st.session_state.all_chats[new_id] = {
                "title": "New Chat",
                "messages": [],
                "created_at": new_id
            }
            st.session_state.current_chat_id = new_id
            st.query_params["chat_id"] = new_id
            save_chats()
            st.rerun()