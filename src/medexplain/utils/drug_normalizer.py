"""
Drug Name Normalizer for MedExplain
Handles brand names, generics, and common misspellings
"""

from typing import Dict, List, Optional, Tuple
import re
from difflib import get_close_matches


class DrugNameNormalizer:
    """Normalizes drug names to standard forms and handles aliases"""
    
    def __init__(self):
        # Common brand name to generic mappings
        self.brand_to_generic = {
            # Pain relievers
            "advil": "ibuprofen",
            "motrin": "ibuprofen", 
            "tylenol": "acetaminophen",
            "aspirin": "aspirin",
            "aleve": "naproxen",
            
            # Heart medications
            "prinivil": "lisinopril",
            "zestril": "lisinopril",
            "norvasc": "amlodipine",
            "lopressor": "metoprolol",
            "toprol": "metoprolol",
            "cozaar": "losartan",
            
            # Diabetes
            "glucophage": "metformin",
            "fortamet": "metformin",
            "ozempic": "semaglutide",
            "wegovy": "semaglutide",
            "rybelsus": "semaglutide",
            
            # Mental health
            "zoloft": "sertraline",
            "lexapro": "escitalopram",
            "prozac": "fluoxetine",
            "cymbalta": "duloxetine",
            "wellbutrin": "bupropion",
            "xanax": "alprazolam",
            "ativan": "lorazepam",
            "klonopin": "clonazepam",
            "valium": "diazepam",
            
            # Respiratory  
            "proventil": "albuterol",
            "ventolin": "albuterol",
            "singulair": "montelukast",
            "flovent": "fluticasone",
            
            # Stomach
            "prilosec": "omeprazole",
            "prevacid": "lansoprazole",
            "nexium": "esomeprazole",
            "protonix": "pantoprazole",
            "pepcid": "famotidine",
            "zantac": "ranitidine",
            
            # Cholesterol
            "lipitor": "atorvastatin",
            "crestor": "rosuvastatin",
            "zocor": "simvastatin",
            "pravachol": "pravastatin",
            
            # Antibiotics
            "amoxil": "amoxicillin",
            "augmentin": "amoxicillin",
            "zpack": "azithromycin",
            "zithromax": "azithromycin",
            "cipro": "ciprofloxacin",
            "levaquin": "levofloxacin",
            "keflex": "cephalexin",
            "bactrim": "sulfamethoxazole",
            
            # Sleep
            "ambien": "zolpidem",
            "lunesta": "eszopiclone",
            "sonata": "zaleplon",
            
            # Allergy
            "claritin": "loratadine",
            "zyrtec": "cetirizine", 
            "allegra": "fexofenadine",
            "benadryl": "diphenhydramine",
            
            # Blood thinners
            "coumadin": "warfarin",
            "eliquis": "apixaban",
            "xarelto": "rivaroxaban",
            "plavix": "clopidogrel",
            
            # Thyroid
            "synthroid": "levothyroxine",
            "levoxyl": "levothyroxine",
            
            # Others
            "neurontin": "gabapentin",
            "lyrica": "pregabalin",
            "tramadol": "tramadol",
            "percocet": "oxycodone",
            "vicodin": "hydrocodone",
            "panadol": "acetaminophen",
            "excedrin": "acetaminophen",
            "feverall": "acetaminophen",
            "paracetamol": "acetaminophen",  # International name
            "paracetomol": "acetaminophen",  # Common misspelling
        }
        
        # Common misspellings and international variants
        self.common_misspellings = {
            # Ibuprofen variants
            "ibuprofin": "ibuprofen",
            "ibuprophen": "ibuprofen",
            "ibuprofen": "ibuprofen",
            
            # Acetaminophen/Paracetamol variants
            "acetominophen": "acetaminophen",
            "acetaminaphen": "acetaminophen",
            "paracetomol": "acetaminophen",
            "paracetamol": "acetaminophen",
            "paracetomol": "acetaminophen",
            "parcetamol": "acetaminophen",
            
            # Other common misspellings
            "lisinpril": "lisinopril",
            "lisinopril": "lisinopril",
            "metformin": "metformin",
            "metphormin": "metformin",
            "amlodapine": "amlodipine",
            "amlodipene": "amlodipine",
            "omeprazol": "omeprazole",
            "omeprozole": "omeprazole",
            "sertralin": "sertraline",
            "sertraline": "sertraline",
            "gabapenten": "gabapentin",
            "gabapentin": "gabapentin",
            
            # International variants
            "diclofenac": "diclofenac",
            "naproxen": "naproxen",
            "asprin": "aspirin",
            "asiprin": "aspirin",
        }
        
        # All known drug names (combine generics and brands)
        self.all_known_drugs = set()
        self.all_known_drugs.update(self.brand_to_generic.keys())
        self.all_known_drugs.update(self.brand_to_generic.values())
        self.all_known_drugs.update(self.common_misspellings.keys())
        self.all_known_drugs.update(self.common_misspellings.values())
    
    def normalize_drug_name(self, drug_name: str) -> str:
        """Convert any drug name to its standard generic form"""
        if not drug_name:
            return ""
        
        # Clean input
        cleaned = drug_name.lower().strip()
        cleaned = re.sub(r'[^a-z]', '', cleaned)  # Remove non-letters
        
        # Check exact matches first
        if cleaned in self.brand_to_generic:
            return self.brand_to_generic[cleaned].title()
        
        if cleaned in self.common_misspellings:
            return self.common_misspellings[cleaned].title()
        
        # Return as-is if already generic or unknown
        return drug_name.title()
    
    def suggest_corrections(self, drug_name: str, limit: int = 3) -> List[str]:
        """Suggest close matches for misspelled drug names"""
        if not drug_name:
            return []
        
        cleaned = drug_name.lower().strip()
        
        # Use difflib for fuzzy matching
        matches = get_close_matches(
            cleaned, 
            self.all_known_drugs, 
            n=limit, 
            cutoff=0.6
        )
        
        # Normalize suggestions
        suggestions = []
        for match in matches:
            normalized = self.normalize_drug_name(match)
            if normalized not in suggestions:
                suggestions.append(normalized)
        
        return suggestions[:limit]
    
    def extract_and_normalize(self, text: str) -> Tuple[str, List[str]]:
        """Extract drug name from text and provide normalized form + suggestions"""
        # Clean the text and remove command prefixes
        cleaned_text = text.lower().strip()
        
        # Remove common command prefixes
        command_prefixes = ['/explain', '/compare', '/interactions', '/dosage', 'explain', 'compare']
        for prefix in command_prefixes:
            if cleaned_text.startswith(prefix):
                cleaned_text = cleaned_text[len(prefix):].strip()
                break
        
        # Extract words from cleaned text
        words = re.findall(r'\b[a-zA-Z]{3,}\b', cleaned_text)
        
        # Priority 1: Look for exact matches with known drugs
        for word in words:
            if word in self.all_known_drugs:
                normalized = self.normalize_drug_name(word)
                suggestions = self.suggest_corrections(word)
                return normalized, suggestions
        
        # Priority 2: Look for fuzzy matches with known drugs
        for word in words:
            if len(word) >= 4:
                fuzzy_matches = get_close_matches(word, self.all_known_drugs, n=1, cutoff=0.8)
                if fuzzy_matches:
                    normalized = self.normalize_drug_name(fuzzy_matches[0])
                    suggestions = self.suggest_corrections(word)
                    return normalized, suggestions
        
        # Priority 3: Use pattern-based extraction with better filtering
        exclude_words = {
            'what', 'does', 'the', 'side', 'effects', 'uses', 'about', 'is', 'are',
            'tell', 'me', 'how', 'can', 'will', 'should', 'would', 'could', 'have',
            'that', 'this', 'they', 'them', 'with', 'from', 'take', 'taking',
            'medication', 'medicine', 'drug', 'pill', 'tablet', 'used', 'help',
            'love', 'like', 'hate', 'need', 'want', 'times', 'day', 'daily',
            'much', 'many', 'often', 'long', 'safe', 'dangerous', 'good', 'bad'
        }
        
        patterns = [
            r"(?:about|of|is|tell me about|what is)\s+([a-zA-Z]+)",
            r"([a-zA-Z]+)\s+(?:side effects|uses|dosage|contraindications)",
            r"(?:what does|what is)\s+([a-zA-Z]+)",
            r"(?:does|do)\s+([a-zA-Z]+)\s+(?:do|does|work)",
            r"\b([a-zA-Z]{5,})\b",  # Longer words more likely to be drugs
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                cleaned = match.strip().lower()
                if cleaned not in exclude_words and len(cleaned) >= 4:
                    # Check if it looks like a drug name
                    if self.is_valid_drug_name(cleaned):
                        normalized = self.normalize_drug_name(match)
                        suggestions = self.suggest_corrections(match)
                        return normalized, suggestions
        
        return "", []
    
    def is_valid_drug_name(self, drug_name: str) -> bool:
        """Check if a name looks like a valid drug name"""
        if not drug_name or len(drug_name) < 3:
            return False
        
        cleaned = drug_name.lower().strip()
        
        # Check if it's in our known drugs
        if cleaned in self.all_known_drugs:
            return True
        
        # Check if it looks drug-like (ends in common suffixes)
        drug_suffixes = ['ine', 'ol', 'an', 'il', 'one', 'ate', 'ide']
        if any(cleaned.endswith(suffix) for suffix in drug_suffixes):
            return True
        
        # Check minimum length and alpha-only
        if len(cleaned) >= 6 and cleaned.isalpha():
            return True
        
        return False


# Example usage
if __name__ == "__main__":
    normalizer = DrugNameNormalizer()
    
    # Test cases
    test_cases = [
        "what does advil do?",
        "tylenol side effects", 
        "tell me about ibuprofin",  # misspelling
        "zoloft contraindications",
        "acetominophen uses"  # misspelling
    ]
    
    for test in test_cases:
        normalized, suggestions = normalizer.extract_and_normalize(test)
        print(f"Query: {test}")
        print(f"Normalized: {normalized}")
        print(f"Suggestions: {suggestions}")
        print("---")