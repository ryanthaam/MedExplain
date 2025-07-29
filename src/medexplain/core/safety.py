"""
Safety System for MedExplain
Implements safety checks and disclaimers for medical queries
"""

from typing import Dict, List, Any, Optional
import re
from dataclasses import dataclass
from enum import Enum


class QueryType(Enum):
    """Types of medical queries for safety classification"""
    GENERAL_INFO = "general_info"
    DOSAGE = "dosage"
    SIDE_EFFECTS = "side_effects"
    INTERACTIONS = "interactions"
    CONTRAINDICATIONS = "contraindications"
    EMERGENCY = "emergency"
    DIAGNOSIS = "diagnosis"
    DANGEROUS = "dangerous"


@dataclass
class SafetyResult:
    """Result of safety check"""
    is_safe: bool
    query_type: QueryType
    message: str
    confidence: float


class SafetyFilter:
    """Filters dangerous or inappropriate medical queries"""
    
    def __init__(self):
        # Patterns for dangerous queries that should be blocked
        self.dangerous_patterns = [
            r"how much .* to (die|kill|overdose)",
            r"lethal dose",
            r"suicide",
            r"self harm",
            r"how to get high",
            r"recreational use",
            r"abuse",
            r"illegal",
        ]
        
        # Patterns for dosage-related queries (need strong warnings)
        self.dosage_patterns = [
            r"how much .* should i take",
            r"what dose",
            r"dosage for",
            r"how many pills",
            r"mg per day",
            r"frequency",
            r"how often",
        ]
        
        # Emergency patterns
        self.emergency_patterns = [
            r"overdose",
            r"poisoning",
            r"emergency",
            r"urgent",
            r"severe reaction",
            r"allergic reaction",
            r"cant breathe",
            r"chest pain",
            r"heart attack",
            r"stroke",
        ]
        
        # Diagnosis patterns
        self.diagnosis_patterns = [
            r"do i have",
            r"am i sick",
            r"what's wrong with me",
            r"diagnose",
            r"what disease",
            r"what condition",
        ]
    
    def check_query(self, query: str) -> Dict[str, Any]:
        """
        Check if query is safe and classify it
        """
        query_lower = query.lower()
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return {
                    "is_safe": False,
                    "query_type": QueryType.DANGEROUS,
                    "message": self._get_dangerous_response(),
                    "confidence": 0.95
                }
        
        # Check for emergency patterns
        for pattern in self.emergency_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return {
                    "is_safe": False,
                    "query_type": QueryType.EMERGENCY,
                    "message": self._get_emergency_response(),
                    "confidence": 0.9
                }
        
        # Check for diagnosis patterns
        for pattern in self.diagnosis_patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                return {
                    "is_safe": False,
                    "query_type": QueryType.DIAGNOSIS,
                    "message": self._get_diagnosis_response(),
                    "confidence": 0.85
                }
        
        # Classify safe queries
        query_type = self._classify_safe_query(query_lower)
        
        return {
            "is_safe": True,
            "query_type": query_type,
            "message": "Query is safe to process",
            "confidence": 0.8
        }
    
    def _classify_safe_query(self, query: str) -> QueryType:
        """Classify safe queries by type"""
        # Check for dosage patterns
        for pattern in self.dosage_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return QueryType.DOSAGE
        
        # Check for specific content types
        if any(word in query for word in ["side effect", "adverse", "reaction"]):
            return QueryType.SIDE_EFFECTS
        
        if any(word in query for word in ["interaction", "combine", "together"]):
            return QueryType.INTERACTIONS
        
        if any(word in query for word in ["contraindication", "should not", "avoid"]):
            return QueryType.CONTRAINDICATIONS
        
        return QueryType.GENERAL_INFO
    
    def _get_dangerous_response(self) -> str:
        """Response for dangerous queries"""
        return """
I cannot and will not provide information that could be used for self-harm or illegal purposes. 

If you're having thoughts of self-harm, please reach out for help:
• National Suicide Prevention Lifeline: 988
• Crisis Text Line: Text HOME to 741741
• Emergency Services: 911

For legitimate medical questions, please consult with a healthcare professional or rephrase your question to focus on general drug information.
        """.strip()
    
    def _get_emergency_response(self) -> str:
        """Response for emergency situations"""
        return """
⚠️ MEDICAL EMERGENCY WARNING ⚠️

If this is a medical emergency:
• Call 911 immediately
• Contact Poison Control: 1-800-222-1222
• Go to your nearest emergency room

I cannot provide emergency medical advice. This appears to be an urgent situation that requires immediate professional medical attention.

For non-emergency questions about medications, I'm here to help with general drug information from FDA sources.
        """.strip()
    
    def _get_diagnosis_response(self) -> str:
        """Response for diagnosis-seeking queries"""
        return """
I cannot provide medical diagnoses or determine what medical conditions you may have. Only qualified healthcare professionals can diagnose medical conditions through proper examination and testing.

If you have health concerns:
• Consult your doctor or healthcare provider
• Call a nurse hotline if available through your insurance
• Visit an urgent care center for non-emergency concerns
• Go to the emergency room for serious symptoms

I can help you understand general information about medications and their FDA-approved uses, but this should not be used for self-diagnosis.
        """.strip()


class SafetyDisclaimer:
    """Generates appropriate safety disclaimers for different query types"""
    
    def get_disclaimer_for_query(self, query: str, query_type: QueryType = None) -> str:
        """Get appropriate disclaimer based on query type"""
        if query_type is None:
            safety_filter = SafetyFilter()
            result = safety_filter.check_query(query)
            query_type = result["query_type"]
        
        if query_type == QueryType.DOSAGE:
            return self.get_dosage_disclaimer()
        elif query_type in [QueryType.SIDE_EFFECTS, QueryType.INTERACTIONS, QueryType.CONTRAINDICATIONS]:
            return self.get_safety_disclaimer()
        else:
            return self.get_general_disclaimer()
    
    def get_general_disclaimer(self) -> str:
        """General medical disclaimer"""
        return """
⚠️ IMPORTANT DISCLAIMER: This information is for educational purposes only and is not medical advice. Always consult your healthcare provider before starting, stopping, or changing any medication. This information comes from FDA sources but should not replace professional medical consultation.
        """.strip()
    
    def get_dosage_disclaimer(self) -> str:
        """Disclaimer for dosage-related queries"""
        return """
⚠️ DOSAGE WARNING: I cannot provide specific dosing recommendations. Medication dosages must be determined by a licensed healthcare provider based on your individual medical history, current health status, other medications, and specific condition. Taking incorrect doses can be dangerous. Always follow your doctor's instructions and prescription labels.
        """.strip()
    
    def get_safety_disclaimer(self) -> str:
        """Disclaimer for safety-related information"""
        return """
⚠️ SAFETY INFORMATION: This information about side effects, interactions, and contraindications is from FDA sources for educational purposes. Your individual risk factors may differ. Always inform your healthcare provider about all medications, supplements, and health conditions. Seek immediate medical attention if you experience serious adverse reactions.
        """.strip()
    
    def get_emergency_disclaimer(self) -> str:
        """Disclaimer for emergency situations"""
        return """
🚨 EMERGENCY DISCLAIMER: If you are experiencing a medical emergency, call 911 immediately. Do not rely on this chatbot for emergency medical advice. Contact emergency services or poison control (1-800-222-1222) for urgent situations.
        """.strip()


# Example usage and testing
if __name__ == "__main__":
    safety_filter = SafetyFilter()
    disclaimer = SafetyDisclaimer()
    
    # Test queries
    test_queries = [
        "What are the side effects of ibuprofen?",  # Safe
        "How much ibuprofen should I take?",  # Dosage warning
        "How to overdose on acetaminophen?",  # Dangerous - should be blocked
        "I think I'm having an allergic reaction",  # Emergency
        "Do I have cancer?",  # Diagnosis seeking
        "What is metformin used for?",  # General info
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 40)
        
        result = safety_filter.check_query(query)
        print(f"Safe: {result['is_safe']}")
        print(f"Type: {result['query_type']}")
        print(f"Confidence: {result['confidence']}")
        
        if not result['is_safe']:
            print(f"Response: {result['message']}")
        else:
            disc = disclaimer.get_disclaimer_for_query(query, result['query_type'])
            print(f"Disclaimer: {disc}")
        
        print("=" * 50)