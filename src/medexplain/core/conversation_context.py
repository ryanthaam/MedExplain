"""
Conversational Context Manager for MedExplain
Handles follow-up questions and conversational references
"""

import re
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta


class ConversationContext:
    """Manages conversational context for follow-up questions"""
    
    def __init__(self):
        self.recent_drugs = []  # List of recently mentioned drugs
        self.last_query_time = None
        self.conversation_timeout = 300  # 5 minutes
        
        # Patterns that indicate follow-up questions
        self.followup_patterns = [
            # Direct references
            r"can i take it with",
            r"take it together with",
            r"combine it with",
            r"mix it with",
            r"use it with",
            
            # Pronoun references
            r"can i take this with",
            r"take this together with",
            r"combine this with",
            r"mix this with",
            
            # Contextual references
            r"can i take that with",
            r"take that together with",
            r"combine that with",
            
            # Simple combinations
            r"^with ",  # Starting with "with"
            r"together with",
            r"along with",
            
            # "What about" patterns
            r"what about with",
            r"what about",
            r"how about with",  
            r"how about",
            r"and with",
        ]
        
        # Common interaction question starters
        self.interaction_starters = [
            "can i take",
            "is it safe to take",
            "can i combine",
            "can i mix",
            "is it okay to take",
            "safe to combine",
            "okay to mix",
        ]
    
    def add_drug_mention(self, drug_name: str):
        """Add a drug to the recent conversation context"""
        if drug_name and len(drug_name) > 2:
            # Clean the drug name
            cleaned_drug = drug_name.strip().title()
            
            # Add to recent drugs (keep last 3)
            if cleaned_drug not in self.recent_drugs:
                self.recent_drugs.insert(0, cleaned_drug)
                self.recent_drugs = self.recent_drugs[:3]  # Keep only last 3
            
            self.last_query_time = datetime.now()
    
    def is_followup_question(self, query: str) -> bool:
        """Check if this is a follow-up question"""
        if not self.recent_drugs or not self._is_context_valid():
            return False
        
        query_lower = query.lower().strip()
        
        # Check for follow-up patterns
        return any(re.search(pattern, query_lower) for pattern in self.followup_patterns)
    
    def extract_followup_interaction(self, query: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract drugs from a follow-up interaction question"""
        if not self.is_followup_question(query) or not self.recent_drugs:
            return None, None
        
        query_lower = query.lower().strip()
        
        # Get the most recent drug as the first drug
        primary_drug = self.recent_drugs[0]
        
        # Extract the second drug from the query
        secondary_drug = self._extract_secondary_drug(query_lower)
        
        if secondary_drug:
            return primary_drug, secondary_drug
        
        return None, None
    
    def _extract_secondary_drug(self, query: str) -> Optional[str]:
        """Extract the second drug from a follow-up query"""
        # Patterns to extract the secondary drug
        patterns = [
            r"(?:with|and|together with|along with)\s+([a-zA-Z]+)",
            r"(?:take it|take this|take that)\s+(?:with|and)\s+([a-zA-Z]+)",
            r"(?:combine it|combine this|combine that)\s+(?:with|and)\s+([a-zA-Z]+)",
            # For "what about with X" patterns
            r"(?:what about|how about)\s+(?:with|and)\s+([a-zA-Z]+)",
            r"(?:what about|how about)\s+([a-zA-Z]+)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                drug_candidate = match.group(1).strip()
                
                # Filter out common non-drug words
                exclude_words = {
                    'food', 'water', 'milk', 'alcohol', 'coffee', 'tea',
                    'other', 'another', 'something', 'anything', 'nothing',
                    'me', 'you', 'it', 'this', 'that', 'them', 'they'
                }
                
                if drug_candidate.lower() not in exclude_words and len(drug_candidate) >= 3:
                    return drug_candidate.title()
        
        return None
    
    def _is_context_valid(self) -> bool:
        """Check if the conversation context is still valid"""
        if not self.last_query_time:
            return False
        
        time_since_last = datetime.now() - self.last_query_time
        return time_since_last.total_seconds() < self.conversation_timeout
    
    def get_recent_drugs(self) -> List[str]:
        """Get list of recently mentioned drugs"""
        if self._is_context_valid():
            return self.recent_drugs.copy()
        return []
    
    def clear_context(self):
        """Clear the conversation context"""
        self.recent_drugs = []
        self.last_query_time = None
    
    def suggest_clarification(self, query: str) -> str:
        """Suggest clarification for ambiguous follow-up questions"""
        recent = self.get_recent_drugs()
        
        if len(recent) == 1:
            return f"Did you mean: Can I take {recent[0]} with the medication you asked about?"
        elif len(recent) > 1:
            drugs_list = ", ".join(recent[:-1]) + f", or {recent[-1]}"
            return f"Which medication did you mean? Recently we discussed: {drugs_list}"
        else:
            return "I'd be happy to help with drug interactions! Could you specify which medications you'd like to ask about?"


class SmartInteractionDetector:
    """Enhanced interaction detector with conversational awareness"""
    
    def __init__(self):
        self.context = ConversationContext()
        
        # Enhanced interaction patterns
        self.interaction_patterns = [
            # Standard patterns
            r"can i take (.+?) with (.+?)\?",
            r"(.+?) and (.+?) together",
            r"(.+?) with (.+?) interaction",
            r"combining (.+?) and (.+?)",
            r"take (.+?) and (.+?)",
            r"(.+?) and (.+?) safe",
            r"mix (.+?) with (.+?)",
            r"use (.+?) with (.+?)",
            
            # More natural patterns
            r"is it (?:safe|okay) to (?:take|use) (.+?) (?:with|and) (.+?)\??",
            r"(?:can|should) i (?:combine|mix) (.+?) (?:with|and) (.+?)\??",
            r"what about (.+?) (?:with|and) (.+?)\??",
        ]
    
    def detect_interaction_query(self, query: str, add_to_context: bool = True) -> Tuple[Optional[str], Optional[str]]:
        """Enhanced interaction detection with context awareness"""
        
        # First, check for follow-up questions
        if self.context.is_followup_question(query):
            drug1, drug2 = self.context.extract_followup_interaction(query)
            if drug1 and drug2:
                if add_to_context:
                    self.context.add_drug_mention(drug2)  # Add the new drug to context
                return drug1, drug2
        
        # Standard interaction detection
        query_lower = query.lower().strip()
        
        for pattern in self.interaction_patterns:
            match = re.search(pattern, query_lower)
            if match:
                drug1 = match.group(1).strip()
                drug2 = match.group(2).strip()
                
                # Clean up common noise words
                noise_words = ['the', 'a', 'an', 'my', 'some', 'any']
                drug1 = ' '.join([word for word in drug1.split() if word not in noise_words])
                drug2 = ' '.join([word for word in drug2.split() if word not in noise_words])
                
                if drug1 and drug2 and len(drug1) > 2 and len(drug2) > 2:
                    # Add both drugs to context
                    if add_to_context:
                        self.context.add_drug_mention(drug1)
                        self.context.add_drug_mention(drug2)
                    
                    return drug1.title(), drug2.title()
        
        return None, None
    
    def add_drug_to_context(self, drug_name: str):
        """Manually add a drug to conversational context"""
        self.context.add_drug_mention(drug_name)
    
    def get_context_suggestion(self, query: str) -> Optional[str]:
        """Get suggestion for unclear follow-up questions"""
        if self.context.is_followup_question(query):
            return self.context.suggest_clarification(query)
        return None


# Global instance for the RAG pipeline
smart_detector = SmartInteractionDetector()


# Example usage
if __name__ == "__main__":
    detector = SmartInteractionDetector()
    
    # Simulate a conversation
    print("Conversation simulation:")
    
    # First query - establishes context
    query1 = "What are the side effects of Acetaminophen?"
    detector.add_drug_to_context("Acetaminophen")
    print(f"1. User: {query1}")
    print(f"   Context: {detector.context.get_recent_drugs()}")
    
    # Follow-up query
    query2 = "can i take it together with ibuprofen?"
    drug1, drug2 = detector.detect_interaction_query(query2)
    print(f"2. User: {query2}")
    print(f"   Detected: {drug1} + {drug2}")
    print(f"   Context: {detector.context.get_recent_drugs()}")
    
    # Another follow-up
    query3 = "what about with amoxicillin?"
    drug1, drug2 = detector.detect_interaction_query(query3)
    print(f"3. User: {query3}")
    print(f"   Detected: {drug1} + {drug2}")
    print(f"   Context: {detector.context.get_recent_drugs()}")