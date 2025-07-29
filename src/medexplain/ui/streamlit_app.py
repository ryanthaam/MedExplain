"""
MedExplain Streamlit Chat Interface
Main UI for the MedExplain drug information chatbot
"""

import streamlit as st
import sys
from pathlib import Path
from typing import Dict, Any, List
import time

# Add the project root to the path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.append(str(project_root))

# Import with fallback for different execution contexts
try:
    from src.medexplain.core.rag_pipeline import MedExplainRAG
    from src.medexplain.core.vectorstore import DrugVectorStore
    from src.medexplain.utils.session_manager import LocalSessionManager
except ImportError:
    # If running from different directory, try relative imports
    from medexplain.core.rag_pipeline import MedExplainRAG
    from medexplain.core.vectorstore import DrugVectorStore
    from medexplain.utils.session_manager import LocalSessionManager

# Import settings - not needed in UI for MVP
# from src.medexplain.config.settings import settings


# Page configuration
st.set_page_config(
    page_title="MedExplain - AI Drug Information Assistant",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_resource
def init_rag_system():
    """Initialize the RAG system (cached for performance)"""
    try:
        return MedExplainRAG()
    except Exception as e:
        st.error(f"Error initializing RAG system: {e}")
        return None


@st.cache_resource
def init_session_manager():
    """Initialize session manager (cached for performance)"""
    return LocalSessionManager()


def init_session_state():
    """Initialize Streamlit session state"""
    if "session_id" not in st.session_state:
        session_manager = init_session_manager()
        st.session_state.session_id = session_manager.create_session()
    
    if "conversation_id" not in st.session_state:
        session_manager = init_session_manager()
        st.session_state.conversation_id = session_manager.create_conversation(
            st.session_state.session_id
        )
    
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    if "rag_system" not in st.session_state:
        st.session_state.rag_system = init_rag_system()


def display_sidebar():
    """Display sidebar with navigation and features"""
    st.sidebar.title("💊 MedExplain")
    st.sidebar.markdown("AI-powered drug information from FDA sources")
    
    session_manager = init_session_manager()
    
    # Database status
    st.sidebar.subheader("📊 Database Status")
    try:
        vector_store = DrugVectorStore()
        stats = vector_store.get_collection_stats()
        st.sidebar.metric("Drugs Available", stats.get("total_drugs", 0))
        st.sidebar.metric("Total Documents", stats.get("total_documents", 0))
        
        # Show some available drugs
        if stats.get("drugs"):
            with st.sidebar.expander("Available Drugs (Sample)"):
                for drug in stats["drugs"][:10]:
                    st.write(f"• {drug}")
    except Exception as e:
        st.sidebar.error(f"Database connection error: {e}")
    
    # Conversation history
    st.sidebar.subheader("💬 Recent Conversations")
    try:
        conversations = session_manager.get_session_conversations(
            st.session_state.session_id, limit=5
        )
        
        if conversations:
            for conv in conversations:
                # Create a button for each conversation
                if st.sidebar.button(
                    conv.title, 
                    key=f"conv_{conv.id}",
                    help=f"Started: {conv.created_at[:16]}"
                ):
                    # Switch to this conversation
                    st.session_state.conversation_id = conv.id
                    # Load messages
                    st.session_state.messages = []
                    for msg in conv.messages:
                        st.session_state.messages.append({
                            "role": "user" if msg.is_user else "assistant",
                            "content": msg.content,
                            "metadata": msg.metadata or {}
                        })
                    st.rerun()
        else:
            st.sidebar.write("No conversations yet")
    except Exception as e:
        st.sidebar.error(f"Error loading conversations: {e}")
    
    # New conversation button
    if st.sidebar.button("🆕 New Conversation"):
        session_manager = init_session_manager()
        st.session_state.conversation_id = session_manager.create_conversation(
            st.session_state.session_id
        )
        st.session_state.messages = []
        st.rerun()
    
    # Favorite drugs
    st.sidebar.subheader("⭐ Favorite Drugs")
    try:
        favorites = session_manager.get_favorite_drugs(st.session_state.session_id)
        if favorites:
            for drug in favorites:
                col1, col2 = st.sidebar.columns([3, 1])
                with col1:
                    if st.button(drug, key=f"fav_{drug}"):
                        # Quick query about favorite drug
                        query = f"Tell me about {drug}"
                        handle_user_input(query)
                with col2:
                    if st.button("❌", key=f"remove_{drug}"):
                        session_manager.remove_favorite_drug(st.session_state.session_id, drug)
                        st.rerun()
        else:
            st.sidebar.write("No favorites yet")
    except Exception as e:
        st.sidebar.error(f"Error loading favorites: {e}")
    
    # Settings
    st.sidebar.subheader("⚙️ Settings")
    session_manager = init_session_manager()
    preferences = session_manager.get_preferences(st.session_state.session_id)
    
    show_sources = st.sidebar.checkbox(
        "Show Sources", 
        value=preferences.get("show_sources", True)
    )
    detailed_responses = st.sidebar.checkbox(
        "Detailed Responses", 
        value=preferences.get("detailed_responses", True)
    )
    safety_warnings = st.sidebar.checkbox(
        "Safety Warnings", 
        value=preferences.get("safety_warnings", True)
    )
    
    # Update preferences if changed
    new_preferences = {
        "show_sources": show_sources,
        "detailed_responses": detailed_responses,
        "safety_warnings": safety_warnings
    }
    
    if new_preferences != preferences:
        session_manager.update_preferences(st.session_state.session_id, new_preferences)


def display_message(message: Dict[str, Any]):
    """Display a single message in the chat"""
    role = message["role"]
    content = message["content"]
    metadata = message.get("metadata", {})
    
    with st.chat_message(role):
        st.write(content)
        
        # Show metadata for assistant messages
        if role == "assistant" and metadata:
            # Confidence indicator
            if "confidence" in metadata:
                confidence = metadata["confidence"]
                if confidence == "High":
                    st.success(f"🔍 Confidence: {confidence}")
                elif confidence == "Medium":
                    st.warning(f"🔍 Confidence: {confidence}")
                else:
                    st.info(f"🔍 Confidence: {confidence}")
            
            # Safety warning
            if metadata.get("safety_warning"):
                st.error("⚠️ Safety Warning: This query was flagged for safety review")
            
            # Sources
            session_manager = init_session_manager()
            preferences = session_manager.get_preferences(st.session_state.session_id)
            
            if preferences.get("show_sources", True) and "sources" in metadata:
                sources = metadata["sources"]
                if sources:
                    with st.expander("📚 Sources"):
                        for i, source in enumerate(sources, 1):
                            st.write(f"**{i}. {source.get('drug', 'Unknown Drug')}**")
                            st.write(f"Section: {source.get('section', 'Unknown')}")
                            if source.get('url'):
                                st.write(f"[View Source]({source['url']})")
                            if source.get('last_updated'):
                                st.write(f"Last Updated: {source['last_updated']}")
                            if i < len(sources):
                                st.divider()
            
            # Disclaimer
            if "disclaimer" in metadata:
                with st.expander("⚠️ Important Disclaimer"):
                    st.warning(metadata["disclaimer"])
            
            # Add to favorites button
            if "sources" in metadata and metadata["sources"]:
                drugs_mentioned = list(set([
                    source.get('drug') for source in metadata["sources"] 
                    if source.get('drug')
                ]))
                
                if drugs_mentioned:
                    st.write("**Add to favorites:**")
                    cols = st.columns(min(3, len(drugs_mentioned)))
                    for i, drug in enumerate(drugs_mentioned[:3]):
                        with cols[i]:
                            # Create unique key using timestamp and index
                            unique_key = f"add_fav_{drug}_{int(time.time())}_{i}_{len(st.session_state.messages)}"
                            if st.button(f"⭐ {drug}", key=unique_key):
                                session_manager = init_session_manager()
                                session_manager.add_favorite_drug(st.session_state.session_id, drug)
                                st.success(f"Added {drug} to favorites!")
                                time.sleep(1)
                                st.rerun()


def handle_user_input(user_input: str):
    """Handle user input and generate response"""
    if not user_input.strip():
        return
    
    # Add user message to chat
    user_message = {"role": "user", "content": user_input}
    st.session_state.messages.append(user_message)
    
    # Save to session manager
    session_manager = init_session_manager()
    session_manager.add_message(
        st.session_state.conversation_id,
        user_input,
        is_user=True
    )
    
    # Generate response
    rag_system = st.session_state.rag_system
    if rag_system:
        with st.spinner("Thinking..."):
            try:
                # Get user preferences
                preferences = session_manager.get_preferences(st.session_state.session_id)
                
                result = rag_system.query(
                    user_input,
                    include_safety_check=preferences.get("safety_warnings", True)
                )
                
                assistant_message = {
                    "role": "assistant",
                    "content": result["response"],
                    "metadata": {
                        "confidence": result.get("confidence"),
                        "safety_warning": result.get("safety_warning"),
                        "sources": result.get("sources", []),
                        "disclaimer": result.get("disclaimer")
                    }
                }
                
                st.session_state.messages.append(assistant_message)
                
                # Save to session manager
                session_manager.add_message(
                    st.session_state.conversation_id,
                    result["response"],
                    is_user=False,
                    metadata=assistant_message["metadata"]
                )
                
            except Exception as e:
                error_message = {
                    "role": "assistant",
                    "content": f"I apologize, but I encountered an error: {str(e)}",
                    "metadata": {"error": True}
                }
                st.session_state.messages.append(error_message)
                st.error(f"Error: {e}")


def main():
    """Main application"""
    init_session_state()
    
    # Display sidebar
    display_sidebar()
    
    # Main chat interface
    st.title("💊 MedExplain")
    st.subheader("AI-powered drug information from FDA sources")
    
    # Quick start suggestions
    if not st.session_state.messages:
        st.markdown("""
        Welcome to MedExplain! I can help you understand medications using official FDA information. 
        
        **Try asking:**
        - "What are the side effects of ibuprofen?"
        - "What is metformin used for?"
        - "Tell me about lisinopril contraindications"
        - "What should I know about aspirin?"
        """)
        
        # Quick action buttons
        st.subheader("Quick Questions")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("💊 Common Pain Relievers"):
                handle_user_input("Tell me about common over-the-counter pain relievers")
        
        with col2:
            if st.button("❤️ Heart Medications"):
                handle_user_input("What are common heart medications?")
        
        with col3:
            if st.button("🩺 Diabetes Medications"):
                handle_user_input("Tell me about diabetes medications")
    
    # Display chat messages
    for message in st.session_state.messages:
        display_message(message)
    
    # Chat input
    if prompt := st.chat_input("Ask about any medication..."):
        handle_user_input(prompt)
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666;'>
        <small>
            ⚠️ This is for educational purposes only. Always consult your healthcare provider for medical advice.
            <br>
            Information sourced from FDA databases • Not medical advice
        </small>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()