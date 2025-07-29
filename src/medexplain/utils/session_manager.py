"""
Local Session Manager for MedExplain MVP
Handles conversation history and user preferences using local storage
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from pathlib import Path
import uuid
from dataclasses import dataclass, asdict
import pickle


@dataclass
class Message:
    """Single message in conversation"""
    id: str
    content: str
    is_user: bool
    timestamp: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class Conversation:
    """Conversation session with messages"""
    id: str
    title: str
    messages: List[Message]
    created_at: str
    updated_at: str
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class UserSession:
    """User session data"""
    session_id: str
    created_at: str
    last_active: str
    preferences: Dict[str, Any]
    favorite_drugs: List[str]
    conversation_history: List[str]  # List of conversation IDs


class LocalSessionManager:
    """Manages user sessions and conversation history using local files"""
    
    def __init__(self, data_dir: str = "./user_data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.sessions_dir = self.data_dir / "sessions"
        self.conversations_dir = self.data_dir / "conversations"
        self.sessions_dir.mkdir(exist_ok=True)
        self.conversations_dir.mkdir(exist_ok=True)
        
        # Current session tracking
        self.current_session_id = None
        self.current_conversation_id = None
    
    def create_session(self) -> str:
        """Create a new user session"""
        session_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        session = UserSession(
            session_id=session_id,
            created_at=timestamp,
            last_active=timestamp,
            preferences={
                "show_sources": True,
                "detailed_responses": True,
                "safety_warnings": True
            },
            favorite_drugs=[],
            conversation_history=[]
        )
        
        self._save_session(session)
        self.current_session_id = session_id
        return session_id
    
    def get_session(self, session_id: str) -> Optional[UserSession]:
        """Get session by ID"""
        session_file = self.sessions_dir / f"{session_id}.json"
        
        if not session_file.exists():
            return None
        
        try:
            with open(session_file, 'r') as f:
                data = json.load(f)
                return UserSession(**data)
        except Exception as e:
            print(f"Error loading session {session_id}: {e}")
            return None
    
    def update_session_activity(self, session_id: str):
        """Update last active timestamp for session"""
        session = self.get_session(session_id)
        if session:
            session.last_active = datetime.now().isoformat()
            self._save_session(session)
    
    def _save_session(self, session: UserSession):
        """Save session to file"""
        session_file = self.sessions_dir / f"{session.session_id}.json"
        try:
            with open(session_file, 'w') as f:
                json.dump(asdict(session), f, indent=2)
        except Exception as e:
            print(f"Error saving session: {e}")
    
    def create_conversation(self, session_id: str, title: str = None) -> str:
        """Create a new conversation"""
        conversation_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        
        if not title:
            title = f"Conversation {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        conversation = Conversation(
            id=conversation_id,
            title=title,
            messages=[],
            created_at=timestamp,
            updated_at=timestamp,
            metadata={"session_id": session_id}
        )
        
        self._save_conversation(conversation)
        
        # Add to session history
        session = self.get_session(session_id)
        if session:
            session.conversation_history.append(conversation_id)
            self._save_session(session)
        
        self.current_conversation_id = conversation_id
        return conversation_id
    
    def add_message(self, conversation_id: str, content: str, is_user: bool, metadata: Dict[str, Any] = None) -> str:
        """Add message to conversation"""
        conversation = self.get_conversation(conversation_id)
        if not conversation:
            return None
        
        message_id = str(uuid.uuid4())
        message = Message(
            id=message_id,
            content=content,
            is_user=is_user,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        
        conversation.messages.append(message)
        conversation.updated_at = datetime.now().isoformat()
        
        # Auto-update title based on first user message
        if is_user and len([m for m in conversation.messages if m.is_user]) == 1:
            conversation.title = self._generate_title(content)
        
        self._save_conversation(conversation)
        return message_id
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get conversation by ID"""
        conv_file = self.conversations_dir / f"{conversation_id}.json"
        
        if not conv_file.exists():
            return None
        
        try:
            with open(conv_file, 'r') as f:
                data = json.load(f)
                # Convert message dicts back to Message objects
                messages = [Message(**msg) for msg in data['messages']]
                data['messages'] = messages
                return Conversation(**data)
        except Exception as e:
            print(f"Error loading conversation {conversation_id}: {e}")
            return None
    
    def _save_conversation(self, conversation: Conversation):
        """Save conversation to file"""
        conv_file = self.conversations_dir / f"{conversation.id}.json"
        try:
            # Convert to dict for JSON serialization
            conv_dict = asdict(conversation)
            with open(conv_file, 'w') as f:
                json.dump(conv_dict, f, indent=2)
        except Exception as e:
            print(f"Error saving conversation: {e}")
    
    def get_session_conversations(self, session_id: str, limit: int = 50) -> List[Conversation]:
        """Get conversations for a session"""
        session = self.get_session(session_id)
        if not session:
            return []
        
        conversations = []
        for conv_id in session.conversation_history[-limit:]:
            conv = self.get_conversation(conv_id)
            if conv:
                conversations.append(conv)
        
        # Sort by updated time (most recent first)
        conversations.sort(key=lambda x: x.updated_at, reverse=True)
        return conversations
    
    def add_favorite_drug(self, session_id: str, drug_name: str):
        """Add drug to user's favorites"""
        session = self.get_session(session_id)
        if session and drug_name not in session.favorite_drugs:
            session.favorite_drugs.append(drug_name)
            self._save_session(session)
    
    def remove_favorite_drug(self, session_id: str, drug_name: str):
        """Remove drug from user's favorites"""
        session = self.get_session(session_id)
        if session and drug_name in session.favorite_drugs:
            session.favorite_drugs.remove(drug_name)
            self._save_session(session)
    
    def get_favorite_drugs(self, session_id: str) -> List[str]:
        """Get user's favorite drugs"""
        session = self.get_session(session_id)
        return session.favorite_drugs if session else []
    
    def update_preferences(self, session_id: str, preferences: Dict[str, Any]):
        """Update user preferences"""
        session = self.get_session(session_id)
        if session:
            session.preferences.update(preferences)
            self._save_session(session)
    
    def get_preferences(self, session_id: str) -> Dict[str, Any]:
        """Get user preferences"""
        session = self.get_session(session_id)
        return session.preferences if session else {}
    
    def _generate_title(self, first_message: str) -> str:
        """Generate conversation title from first message"""
        # Simple title generation - take first few words
        words = first_message.split()[:6]
        title = " ".join(words)
        if len(title) > 50:
            title = title[:47] + "..."
        return title
    
    def delete_conversation(self, conversation_id: str, session_id: str):
        """Delete a conversation"""
        # Remove from session history
        session = self.get_session(session_id)
        if session and conversation_id in session.conversation_history:
            session.conversation_history.remove(conversation_id)
            self._save_session(session)
        
        # Delete conversation file
        conv_file = self.conversations_dir / f"{conversation_id}.json"
        if conv_file.exists():
            conv_file.unlink()
    
    def cleanup_old_sessions(self, days: int = 30):
        """Clean up sessions older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        for session_file in self.sessions_dir.glob("*.json"):
            try:
                with open(session_file, 'r') as f:
                    data = json.load(f)
                    last_active = datetime.fromisoformat(data['last_active'])
                    
                    if last_active < cutoff_date:
                        # Delete session and its conversations
                        session_id = data['session_id']
                        for conv_id in data.get('conversation_history', []):
                            conv_file = self.conversations_dir / f"{conv_id}.json"
                            if conv_file.exists():
                                conv_file.unlink()
                        
                        session_file.unlink()
                        print(f"Cleaned up old session: {session_id}")
                        
            except Exception as e:
                print(f"Error cleaning up session {session_file}: {e}")
    
    def get_session_stats(self, session_id: str) -> Dict[str, Any]:
        """Get statistics for a session"""
        session = self.get_session(session_id)
        if not session:
            return {}
        
        conversations = self.get_session_conversations(session_id)
        total_messages = sum(len(conv.messages) for conv in conversations)
        user_messages = sum(len([m for m in conv.messages if m.is_user]) for conv in conversations)
        
        return {
            "session_id": session_id,
            "created_at": session.created_at,
            "last_active": session.last_active,
            "total_conversations": len(conversations),
            "total_messages": total_messages,
            "user_messages": user_messages,
            "favorite_drugs_count": len(session.favorite_drugs),
            "preferences": session.preferences
        }


# Example usage
if __name__ == "__main__":
    # Initialize session manager
    manager = LocalSessionManager()
    
    # Create a session
    session_id = manager.create_session()
    print(f"Created session: {session_id}")
    
    # Create a conversation
    conv_id = manager.create_conversation(session_id)
    print(f"Created conversation: {conv_id}")
    
    # Add messages
    manager.add_message(conv_id, "What are the side effects of ibuprofen?", is_user=True)
    manager.add_message(conv_id, "Ibuprofen can cause stomach upset, nausea...", is_user=False, 
                       metadata={"confidence": "High", "sources": ["FDA"]})
    
    # Get conversation
    conversation = manager.get_conversation(conv_id)
    print(f"Conversation title: {conversation.title}")
    print(f"Messages: {len(conversation.messages)}")
    
    # Add favorite drug
    manager.add_favorite_drug(session_id, "Ibuprofen")
    
    # Get stats
    stats = manager.get_session_stats(session_id)
    print(f"Session stats: {stats}")