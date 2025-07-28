import streamlit as st
import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

class GIKIKnowledgeBase:
    def __init__(self):
        # Basic information about GIKI
        self.basic_info = {
            "name": "Ghulam Ishaq Khan Institute of Engineering Sciences and Technology",
            "location": "Topi, Khyber Pakhtunkhwa, Pakistan",
            "established": "1993",
            "type": "Private university",
            "campus": "400 acres"
        }
        
        # Academic programs
        self.programs = {
            "undergraduate": [
                "Computer Engineering",
                "Electrical Engineering",
                "Mechanical Engineering",
                "Chemical Engineering",
                "Materials Engineering",
                "Industrial Engineering",
                "Faculty of Computer Sciences and Engineering",
                "Faculty of Engineering Sciences",
                "Faculty of Materials and Chemical Engineering"
            ]
        }
        
        # Events calendar
        self.events = {
            "upcoming": [
                {
                    "name": "Spring Break",
                    "date": "March 25-29, 2024",
                    "description": "Spring semester break for all students"
                },
                {
                    "name": "Final Examinations",
                    "date": "May 20-31, 2024",
                    "description": "Spring semester final examinations"
                },
                {
                    "name": "Graduation Ceremony",
                    "date": "June 15, 2024",
                    "description": "Annual graduation ceremony for the Class of 2024"
                }
            ],
            "annual": [
                {
                    "name": "GIKI Sports Gala",
                    "usual_month": "February-March",
                    "description": "Annual sports competition between departments"
                },
                {
                    "name": "Job Fair",
                    "usual_month": "April",
                    "description": "Annual job fair connecting students with potential employers"
                }
            ]
        }
        
        # Facilities
        self.facilities = {
            "academic": [
                "Central Library",
                "Computer Labs",
                "Engineering Labs",
                "Research Centers",
                "Lecture Halls"
            ],
            "residential": [
                "Male Hostels",
                "Female Hostels",
                "Faculty Housing"
            ],
            "recreational": [
                "Sports Complex",
                "Gymnasium",
                "Cricket Ground",
                "Football Ground",
                "Basketball Courts"
            ]
        }
        
        # FAQ patterns and responses
        self.faq_patterns = {
            "what is giki": self._get_basic_info,
            "about giki": self._get_basic_info,
            "where is giki": self._get_location_info,
            "location": self._get_location_info,
            "admission": self._get_admission_info,
            "facilities": self._get_facilities_info,
            "programs": self._get_programs_info,
            "departments": self._get_programs_info,
            "sports": self._get_sports_info,
            "events": self._get_next_event
        }
    
    def _get_basic_info(self) -> str:
        """Returns basic information about GIKI"""
        return f"""GIKI ({self.basic_info['name']}) is a {self.basic_info['type']} established in {self.basic_info['established']}.
        It is located in {self.basic_info['location']} with a campus size of {self.basic_info['campus']}."""
    
    def _get_location_info(self) -> str:
        """Returns location information"""
        return f"GIKI is located in {self.basic_info['location']}. The campus spans {self.basic_info['campus']}."
    
    def _get_admission_info(self) -> str:
        """Returns admission-related information"""
        return """Admission to GIKI is based on the following criteria:
        1. GIKI Entry Test
        2. Academic Record
        3. Interview (for shortlisted candidates)
        
        The admission process usually starts in June-July each year."""
    
    def _get_facilities_info(self) -> str:
        """Returns information about GIKI facilities"""
        facilities_str = "GIKI offers the following facilities:\n\n"
        for category, items in self.facilities.items():
            facilities_str += f"{category.title()}:\n"
            facilities_str += "\n".join(f"- {item}" for item in items)
            facilities_str += "\n\n"
        return facilities_str
    
    def _get_programs_info(self) -> str:
        """Returns information about academic programs"""
        programs_str = "GIKI offers the following undergraduate programs:\n\n"
        programs_str += "\n".join(f"- {program}" for program in self.programs["undergraduate"])
        return programs_str
    
    def _get_sports_info(self) -> str:
        """Returns information about sports facilities and events"""
        return """GIKI has excellent sports facilities including:
        - Sports Complex with indoor games
        - Gymnasium
        - Cricket Ground
        - Football Ground
        - Basketball Courts
        
        The annual Sports Gala is held in February-March."""
    
    def _get_next_event(self) -> str:
        """Returns information about the next upcoming event"""
        if self.events["upcoming"]:
            next_event = self.events["upcoming"][0]
            return f"The next event is {next_event['name']} scheduled for {next_event['date']}. {next_event['description']}"
        return "No upcoming events are currently scheduled."
    
    def get_response(self, query: str) -> str:
        """Generate a response based on the query"""
        query = query.lower().strip()
        
        # Check for patterns in FAQ
        for pattern, response_func in self.faq_patterns.items():
            if pattern in query:
                return response_func()
        
        # Default response if no pattern matches
        return """I can help you with information about:
        - Basic information about GIKI
        - Location and campus details
        - Admission process
        - Available facilities
        - Academic programs
        - Sports facilities
        - Upcoming events
        
        Please ask about any of these topics!"""

class ChatManager:
    def __init__(self):
        self.DATA_DIR = Path("chat_data")
        self.DATA_DIR.mkdir(exist_ok=True)
        self.DATA_FILE = self.DATA_DIR / "chat_history.json"
        self.knowledge_base = GIKIKnowledgeBase()
    
    def generate_chat_id(self) -> str:
        """Generate a unique chat ID based on timestamp"""
        return str(int(time.time() * 1000))
    
    def format_timestamp(self, timestamp: str) -> str:
        """Format timestamp for display"""
        try:
            return datetime.fromtimestamp(int(timestamp)/1000).strftime('%b %d %H:%M')
        except:
            return "Unknown time"
    
    def load_chats(self) -> Dict:
        """Load chat history with error handling"""
        if self.DATA_FILE.exists():
            try:
                with open(self.DATA_FILE, "r") as f:
                    chats = json.load(f)
                    # Ensure all chats have required fields
                    for chat_id, chat in chats.items():
                        if "created_at" not in chat:
                            chat["created_at"] = chat_id if chat_id.isdigit() else self.generate_chat_id()
                        if "title" not in chat:
                            chat["title"] = "Untitled Chat"
                        if "messages" not in chat:
                            chat["messages"] = []
                    return chats
            except Exception as e:
                st.error(f"Error loading chat history: {e}")
                return {}
        return {}
    
    def save_chats(self, chats: Dict) -> bool:
        """Save chat history with error handling"""
        try:
            with open(self.DATA_FILE, "w") as f:
                json.dump(chats, f, indent=2)
            return True
        except Exception as e:
            st.error(f"Error saving chat history: {e}")
            return False
    
    def delete_chat(self, chat_id: str, chats: Dict) -> bool:
        """Delete a chat from history"""
        try:
            if chat_id in chats:
                del chats[chat_id]
                return self.save_chats(chats)
            return False
        except Exception as e:
            st.error(f"Error deleting chat: {e}")
            return False
    
    def get_response(self, query: str) -> str:
        """Get response from knowledge base"""
        return self.knowledge_base.get_response(query)

# Initialize chat manager
chat_manager = ChatManager()

# Initialize session state
if "all_chats" not in st.session_state:
    st.session_state.all_chats = chat_manager.load_chats()
if "current_chat_id" not in st.session_state:
    st.session_state.current_chat_id = None
if "show_delete_confirm" not in st.session_state:
    st.session_state.show_delete_confirm = None

# Handle URL params
url_chat_id = st.query_params.get("chat_id", None)
if url_chat_id and url_chat_id in st.session_state.all_chats:
    st.session_state.current_chat_id = url_chat_id

# Sidebar - Chat List
with st.sidebar:
    st.header("💬 GIKI Assistant")
    
    # New Chat Button
    if st.button("＋ New Chat", key="new_chat", use_container_width=True):
        new_id = chat_manager.generate_chat_id()
        st.session_state.all_chats[new_id] = {
            "title": "New Chat",
            "messages": [],
            "created_at": new_id
        }
        st.session_state.current_chat_id = new_id
        st.query_params["chat_id"] = new_id
        chat_manager.save_chats(st.session_state.all_chats)
        st.rerun()
    
    st.divider()
    
    if not st.session_state.all_chats:
        st.markdown('<div class="empty-state">No conversations yet</div>', unsafe_allow_html=True)
    else:
        # Sort chats by creation time
        sorted_chats = sorted(
            st.session_state.all_chats.items(),
            key=lambda x: int(x[1].get("created_at", 0)),
            reverse=True
        )
        
        for chat_id, chat in sorted_chats:
            is_active = chat_id == st.session_state.current_chat_id
            created_time = chat_manager.format_timestamp(chat.get("created_at", "0"))
            
            col1, col2 = st.columns([4, 1])
            with col1:
                btn = st.button(
                    f"💬 {chat['title']}",
                    key=f"chat_btn_{chat_id}",
                    help=f"Created: {created_time}",
                    type="secondary" if is_active else "tertiary",
                    use_container_width=True
                )
                
                if btn:
                    st.session_state.current_chat_id = chat_id
                    st.query_params["chat_id"] = chat_id
                    st.rerun()
            
            with col2:
                # Delete button with confirmation
                if st.button("🗑️", key=f"delete_{chat_id}", help="Delete chat"):
                    st.session_state.show_delete_confirm = chat_id
            
            # Show delete confirmation
            if st.session_state.show_delete_confirm == chat_id:
                st.warning("Are you sure you want to delete this chat?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Yes", key=f"confirm_delete_{chat_id}", type="primary"):
                        if chat_manager.delete_chat(chat_id, st.session_state.all_chats):
                            if chat_id == st.session_state.current_chat_id:
                                st.session_state.current_chat_id = None
                                st.query_params.clear()
                            st.session_state.show_delete_confirm = None
                            st.rerun()
                with col2:
                    if st.button("No", key=f"cancel_delete_{chat_id}"):
                        st.session_state.show_delete_confirm = None
                        st.rerun()

# Main Chat Area
if st.session_state.current_chat_id:
    current_chat = st.session_state.all_chats[st.session_state.current_chat_id]
    st.title("💬 GIKI Assistant")
    
    # Display chat messages
    for msg in current_chat["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask me anything about GIKI..."):
        # Update chat title if first message
        if not current_chat["messages"] and prompt.strip():
            current_chat["title"] = prompt[:30] + ("..." if len(prompt) > 30 else "")
        
        # Add user message
        current_chat["messages"].append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            try:
                with st.spinner("Thinking..."):
                    response = chat_manager.get_response(prompt)
                    message_placeholder.markdown(response)
                    current_chat["messages"].append({"role": "assistant", "content": response})
            except Exception as e:
                error_msg = f"❌ Error: {str(e)}"
                message_placeholder.error(error_msg)
                current_chat["messages"].append({"role": "assistant", "content": error_msg})
        
        # Update URL and save chat history
        st.query_params["chat_id"] = st.session_state.current_chat_id
        chat_manager.save_chats(st.session_state.all_chats)
        st.rerun()

else:
    # Welcome screen
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("""
        <div class="empty-state">
            <h3>Welcome to GIKI Assistant</h3>
            <p>I can help you with information about GIKI's events, facilities, programs, and more!</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Start Chatting", key="start_chat", use_container_width=True):
            new_id = chat_manager.generate_chat_id()
            st.session_state.all_chats[new_id] = {
                "title": "New Chat",
                "messages": [],
                "created_at": new_id
            }
            st.session_state.current_chat_id = new_id
            st.query_params["chat_id"] = new_id
            chat_manager.save_chats(st.session_state.all_chats)
            st.rerun()