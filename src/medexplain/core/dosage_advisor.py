"""
Dosage Advisory System for MedExplain
Handles dosage-related queries with appropriate safety measures
"""

from typing import Dict, Any, Optional
import re
from ..utils.drug_normalizer import DrugNameNormalizer


class DosageAdvisor:
    """Provides safe dosage guidance while emphasizing professional consultation"""
    
    def __init__(self):
        self.drug_normalizer = DrugNameNormalizer()
        # Import translator with fallback to avoid circular imports
        try:
            from .plain_english_translator import PlainEnglishTranslator
            self.translator = PlainEnglishTranslator()
        except ImportError:
            self.translator = None
        
        # Common dosage patterns to detect
        self.dosage_patterns = [
            r"can i take .* daily",
            r"how often .* take",
            r"how much .* per day",
            r"daily dose",
            r"safe to take .* every day",
            r"long term use",
            r"chronic use",
            r"daily usage",
            r"take .* regularly",
            r"take .* \d+ times",
            r"\d+ times .* day",
            r"take .* multiple times",
            r"overdose",
            r"too much",
            r"maximum dose"
        ]
        
        # General dosage information for common drugs (EDUCATIONAL ONLY)
        self.general_dosage_info = {
            "acetaminophen": {
                "max_daily": "3000-4000mg for adults",
                "frequency": "Every 4-6 hours as needed", 
                "warnings": [
                    "Do not exceed 4000mg (4g) in 24 hours",
                    "Taking more than recommended can cause serious liver damage",
                    "Avoid alcohol while taking acetaminophen",
                    "Check other medications for acetaminophen content"
                ],
                "daily_use_note": "Not recommended for daily long-term use without medical supervision"
            },
            "ibuprofen": {
                "max_daily": "1200-3200mg for adults (with food)",
                "frequency": "Every 6-8 hours as needed",
                "warnings": [
                    "Take with food to reduce stomach irritation",
                    "Do not exceed 3200mg in 24 hours without medical supervision",
                    "Can increase risk of heart attack, stroke, and stomach bleeding",
                    "Not recommended during pregnancy (especially third trimester)"
                ],
                "daily_use_note": "Long-term daily use requires medical monitoring for cardiovascular and GI risks"
            },
            "aspirin": {
                "max_daily": "650-1000mg every 4 hours (max 4000mg/day)",
                "frequency": "Every 4-6 hours as needed",
                "warnings": [
                    "Can cause stomach bleeding",
                    "Not for children/teens with viral infections (Reye's syndrome risk)",
                    "Increases bleeding risk",
                    "Can interact with blood thinners"
                ],
                "daily_use_note": "Low-dose daily aspirin for heart protection requires medical supervision"
            },
            "semaglutide": {
                "max_daily": "ONCE WEEKLY injection only - NOT daily",
                "frequency": "Once per week subcutaneous injection",
                "warnings": [
                    "PRESCRIPTION ONLY - requires doctor supervision",
                    "Can cause severe nausea, vomiting, and diarrhea",
                    "Risk of thyroid tumors and pancreatitis",
                    "Can cause hypoglycemia when combined with other diabetes medications",
                    "NEVER take multiple doses in one day",
                    "DANGEROUS if used for weight loss without medical supervision"
                ],
                "daily_use_note": "CRITICAL: This is a WEEKLY medication. Taking daily or multiple times per day is EXTREMELY DANGEROUS and can cause severe hypoglycemia, hospitalization, or death."
            }
        }
    
    def is_dosage_query(self, question: str) -> bool:
        """Check if the query is asking about dosage/frequency"""
        question_lower = question.lower()
        return any(re.search(pattern, question_lower) for pattern in self.dosage_patterns)
    
    def handle_dosage_query(self, question: str) -> Dict[str, Any]:
        """Handle dosage-related queries with safety emphasis"""
        # Extract drug name
        drug_name, suggestions = self.drug_normalizer.extract_and_normalize(question)
        
        if not drug_name:
            return self._create_general_dosage_response()
        
        drug_lower = drug_name.lower()
        
        # Check if we have general info for this drug
        # Check for the drug or its normalized form
        if drug_lower in self.general_dosage_info:
            return self._create_specific_dosage_response(drug_name, drug_lower, question)
        
        # Check if it's a variant that normalizes to a known drug
        normalized_drug = self.drug_normalizer.normalize_drug_name(drug_name).lower()
        if normalized_drug in self.general_dosage_info:
            return self._create_specific_dosage_response(drug_name, normalized_drug, question)
        else:
            return self._create_unknown_drug_dosage_response(drug_name, suggestions)
    
    def _create_specific_dosage_response(self, drug_name: str, drug_key: str, question: str) -> Dict[str, Any]:
        """Create response for known drug dosage queries"""
        info = self.general_dosage_info[drug_key]
        
        response = f"""
**⚠️ IMPORTANT: This is general information only. Always consult your healthcare provider before starting any medication regimen.**

**General FDA-approved dosage information for {drug_name}:**

🔹 **Typical Adult Dose**: {info['max_daily']}
🔹 **Frequency**: {info['frequency']}

**⚠️ Important Warnings:**
"""
        
        for warning in info['warnings']:
            response += f"• {warning}\n"
        
        response += f"""
**📋 Regarding Daily Use:**
{info['daily_use_note']}

**🏥 You Should Consult Your Doctor If:**
• You need pain relief for more than 10 days
• You have chronic conditions (heart, liver, kidney disease)
• You take other medications
• You experience side effects
• You're pregnant or breastfeeding

**🚨 REMEMBER:** Self-medication can be dangerous. This information is for educational purposes only and does not replace professional medical advice.
"""
        
        # Translate to plain English if translator available
        if self.translator:
            response = self.translator.translate_response(response.strip())
        
        return {
            "response": response.strip() if not self.translator else response,
            "safety_warning": True,
            "confidence": "Medium",
            "sources": [{"drug": drug_name, "section": "General Dosage Information", "url": "FDA Guidelines"}],
            "disclaimer": self._get_dosage_disclaimer(),
            "query": question
        }
    
    def _create_unknown_drug_dosage_response(self, drug_name: str, suggestions: list) -> Dict[str, Any]:
        """Create response for unknown drug dosage queries"""
        response = f"""
**⚠️ DOSAGE SAFETY WARNING**

I cannot provide specific dosage information for {drug_name} as this requires personalized medical assessment.

**🏥 You Must Consult:**
• Your prescribing doctor
• A licensed pharmacist  
• Call your pharmacy's consultation line
• Use official prescribing information

**❌ Never:**
• Guess dosages based on internet information
• Take medications without proper guidance
• Exceed recommended doses
• Share medications with others

**🔍 For accurate dosage information:**
1. Check the medication label/package insert
2. Call your pharmacy
3. Consult your healthcare provider
4. Use official medical resources like FDA.gov
"""
        
        if suggestions:
            response += f"\n\n🤔 **Did you mean:** {', '.join(suggestions)}?"
        
        # Translate to plain English if translator available
        if self.translator:
            response = self.translator.translate_response(response.strip())
        
        return {
            "response": response.strip() if not self.translator else response,
            "safety_warning": True,
            "confidence": "High",
            "sources": [],
            "disclaimer": self._get_dosage_disclaimer(),
            "query": f"Dosage query for {drug_name}"
        }
    
    def _create_general_dosage_response(self) -> Dict[str, Any]:
        """Create general response when no drug is identified"""
        response = """
**⚠️ MEDICATION DOSAGE SAFETY**

For any medication dosage questions, you should **always consult:**

**🏥 Primary Sources:**
• Your prescribing doctor
• Licensed pharmacist
• Official medication packaging/insert
• FDA-approved prescribing information

**📱 Quick Help:**
• Call your pharmacy's consultation line
• Use your insurance's nurse hotline
• Contact your doctor's office

**❌ Important Reminders:**
• Never guess dosages
• Don't rely on internet forums
• Avoid sharing medications
• Don't exceed package directions without medical supervision

**🚨 For emergencies or overdose concerns, call Poison Control: 1-800-222-1222**
"""
        
        # Translate to plain English if translator available
        if self.translator:
            response = self.translator.translate_response(response.strip())
        
        return {
            "response": response.strip() if not self.translator else response,
            "safety_warning": True,
            "confidence": "High",
            "sources": [],
            "disclaimer": self._get_dosage_disclaimer(),
            "query": "General dosage inquiry"
        }
    
    def _get_dosage_disclaimer(self) -> str:
        """Get specific disclaimer for dosage queries"""
        return """
🚨 DOSAGE DISCLAIMER: Medication dosages must be determined by licensed healthcare providers based on your individual medical history, current health status, other medications, age, weight, and specific condition. This information is for educational purposes only and does not constitute medical advice. Always follow your doctor's instructions and prescription labels.
        """.strip()


# Example usage
if __name__ == "__main__":
    advisor = DosageAdvisor()
    
    test_queries = [
        "can i take panadol daily",
        "how much ibuprofen per day",
        "daily aspirin dose",
        "can i take tylenol every day"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("Is dosage query:", advisor.is_dosage_query(query))
        
        if advisor.is_dosage_query(query):
            result = advisor.handle_dosage_query(query)
            print(f"Response preview: {result['response'][:200]}...")
        print("-" * 50)