"""
Multi-Drug Query Parser for MedExplain
Handles queries containing multiple drug names
"""

import re
from typing import List, Tuple, Dict, Any
from .drug_normalizer import DrugNameNormalizer


class MultiDrugParser:
    """Parses and handles queries containing multiple drug names"""
    
    def __init__(self):
        self.drug_normalizer = DrugNameNormalizer()
        
        # Patterns that indicate multiple drug queries
        self.multi_drug_patterns = [
            r'\n',  # Line breaks between drugs
            r',\s*[A-Z]',  # Comma followed by capitalized word
            r'\d+\.\s*[A-Z]',  # Numbered lists
            r'•\s*[A-Z]',  # Bullet points
            r'-\s*[A-Z]',  # Dashes
        ]
    
    def is_multi_drug_query(self, query: str) -> bool:
        """Check if query contains multiple drugs"""
        # Count potential drug names (capitalized words 4+ chars)
        potential_drugs = re.findall(r'\b[A-Z][a-z]{3,}(?:\s+[a-z]+)*\b', query)
        
        # Check for formatting patterns
        has_formatting = any(re.search(pattern, query) for pattern in self.multi_drug_patterns)
        
        return len(potential_drugs) >= 3 or (len(potential_drugs) >= 2 and has_formatting)
    
    def extract_drug_list(self, query: str) -> List[str]:
        """Extract list of drug names from query"""
        # Remove common question words
        cleaned_query = re.sub(r'^(what does?|tell me about|information about)\s+', '', query, flags=re.IGNORECASE)
        cleaned_query = re.sub(r'\s+(do\??)$', '', cleaned_query, flags=re.IGNORECASE)
        
        # Split by various delimiters
        drug_lines = []
        
        # First try line breaks
        if '\n' in cleaned_query:
            drug_lines = [line.strip() for line in cleaned_query.split('\n') if line.strip()]
        else:
            # Try other delimiters
            for delimiter in [',', '•', '-']:
                if delimiter in cleaned_query:
                    drug_lines = [line.strip() for line in cleaned_query.split(delimiter) if line.strip()]
                    break
        
        # If no clear delimiters, try to extract drug names more intelligently
        if not drug_lines:
            drug_lines = [cleaned_query]
        
        # Clean up and normalize each drug name
        drugs = []
        for line in drug_lines:
            # Remove numbering, bullets, etc.
            cleaned_line = re.sub(r'^\d+\.?\s*', '', line)  # Remove numbers
            cleaned_line = re.sub(r'^[•\-]\s*', '', cleaned_line)  # Remove bullets/dashes
            cleaned_line = re.sub(r'^\s*[❤️🧪🧬]\s*.*?:', '', cleaned_line)  # Remove emoji categories
            
            # Extract drug name
            drug_name, _ = self.drug_normalizer.extract_and_normalize(cleaned_line)
            if drug_name and len(drug_name) > 2:
                drugs.append(drug_name)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_drugs = []
        for drug in drugs:
            if drug.lower() not in seen:
                seen.add(drug.lower())
                unique_drugs.append(drug)
        
        return unique_drugs
    
    def create_individual_queries(self, drugs: List[str], original_query: str) -> List[str]:
        """Create individual queries for each drug"""
        # Determine the query type from original question
        query_lower = original_query.lower()
        
        if 'side effects' in query_lower:
            query_template = "What are the side effects of {}?"
        elif 'contraindications' in query_lower:
            query_template = "What are the contraindications for {}?"
        elif 'uses' in query_lower or 'used for' in query_lower:
            query_template = "What is {} used for?"
        elif 'dosage' in query_lower or 'dose' in query_lower:
            query_template = "What is the dosage for {}?"
        elif 'interactions' in query_lower:
            query_template = "What are the drug interactions for {}?"
        else:
            # Default: general information
            query_template = "What does {} do?"
        
        return [query_template.format(drug) for drug in drugs]
    
    def format_combined_response(self, drug_responses: List[Dict[str, Any]], original_query: str) -> Dict[str, Any]:
        """Combine multiple drug responses into a single formatted response"""
        
        if not drug_responses:
            return {
                "response": "I couldn't find information about the requested medications.",
                "safety_warning": False,
                "confidence": "Low",
                "sources": [],
                "disclaimer": "Please consult your healthcare provider for medication information."
            }
        
        # Build combined response
        combined_response = "Here's information about the medications you asked about:\n\n"
        
        all_sources = []
        has_safety_warning = False
        confidence_levels = []
        disclaimers = []
        
        for i, drug_response in enumerate(drug_responses, 1):
            # Extract drug name from query like "What does Ustekinumab do?" -> "Ustekinumab"
            query = drug_response.get('query', f'Drug {i}')
            drug_name = drug_response.get('drug_name', f'Drug {i}')
            
            # If drug_name wasn't set, try to extract from query
            if drug_name == f'Drug {i}':
                # Parse queries like "What does X do?" or "What is X used for?"
                import re
                match = re.search(r'(?:what does|what is)\s+([A-Za-z]+)', query, re.IGNORECASE)
                if match:
                    drug_name = match.group(1)
                else:
                    # Fallback: look for capitalized words that aren't common words
                    words = query.split()
                    common_words = {'what', 'does', 'do', 'is', 'the', 'used', 'for', 'side', 'effects', 'of'}
                    for word in words:
                        if word.strip('?').lower() not in common_words and len(word) > 3 and word[0].isupper():
                            drug_name = word.strip('?')
                            break
            
            combined_response += f"## {i}. {drug_name}\n\n"
            combined_response += drug_response.get('response', 'No information available') + "\n\n"
            
            # Collect metadata
            if drug_response.get('sources'):
                all_sources.extend(drug_response['sources'])
            
            if drug_response.get('safety_warning'):
                has_safety_warning = True
            
            confidence_levels.append(drug_response.get('confidence', 'Low'))
            
            if drug_response.get('disclaimer'):
                disclaimers.append(drug_response['disclaimer'])
            
            # Add separator except for last item
            if i < len(drug_responses):
                combined_response += "---\n\n"
        
        # Determine overall confidence
        if 'High' in confidence_levels:
            overall_confidence = 'High'
        elif 'Medium' in confidence_levels:
            overall_confidence = 'Medium'
        else:
            overall_confidence = 'Low'
        
        # Use first disclaimer or create general one
        overall_disclaimer = disclaimers[0] if disclaimers else "Always consult your healthcare provider for medication information."
        
        return {
            "response": combined_response.strip(),
            "safety_warning": has_safety_warning,
            "confidence": overall_confidence,
            "sources": all_sources,
            "disclaimer": overall_disclaimer,
            "query": original_query,
            "multi_drug_count": len(drug_responses)
        }


# Example usage
if __name__ == "__main__":
    parser = MultiDrugParser()
    
    test_query = """what does Aripiprazole
Quetiapine fumarate
Risperidone
Duloxetine hydrochloride
do?"""
    
    print("Original query:", repr(test_query))
    print("Is multi-drug:", parser.is_multi_drug_query(test_query))
    
    if parser.is_multi_drug_query(test_query):
        drugs = parser.extract_drug_list(test_query)
        print("Extracted drugs:", drugs)
        
        individual_queries = parser.create_individual_queries(drugs, test_query)
        print("Individual queries:")
        for q in individual_queries:
            print(f"  - {q}")