"""
Plain English Translator for MedExplain
Converts complex medical jargon into simple, understandable language
"""

from typing import Dict, List, Tuple
import re
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Import settings with fallback
try:
    from ...config.settings import settings
except ImportError:
    import sys
    from pathlib import Path
    config_path = Path(__file__).parent.parent.parent.parent / "config"
    sys.path.append(str(config_path))
    from settings import settings


class PlainEnglishTranslator:
    """Translates medical jargon into plain English"""
    
    def __init__(self):
        # Medical jargon dictionary for quick translations
        self.jargon_dict = {
            # Common medical terms
            "contraindication": "reason not to use",
            "contraindications": "reasons not to use",
            "adverse effects": "side effects",
            "adverse reactions": "bad reactions",
            "hypersensitivity": "allergic reaction",
            "anaphylaxis": "severe allergic reaction",
            "hepatotoxicity": "liver damage",
            "nephrotoxicity": "kidney damage",
            "cardiotoxicity": "heart damage",
            "myocardial infarction": "heart attack",
            "cerebrovascular accident": "stroke",
            "hypertension": "high blood pressure",
            "hypotension": "low blood pressure",
            "bradycardia": "slow heart rate",
            "tachycardia": "fast heart rate",
            "arrhythmia": "irregular heartbeat",
            "dyspnea": "difficulty breathing",
            "nausea": "feeling sick to your stomach",
            "emesis": "vomiting",
            "diarrhea": "loose stools",
            "constipation": "difficulty having bowel movements",
            "somnolence": "drowsiness",
            "insomnia": "trouble sleeping",
            "vertigo": "dizziness",
            "syncope": "fainting",
            "tremor": "shaking",
            "seizure": "convulsion",
            "edema": "swelling",
            "pruritus": "itching",
            "rash": "skin irritation",
            "urticaria": "hives",
            "photosensitivity": "increased sensitivity to sunlight",
            "xerostomia": "dry mouth",
            
            # Dosage terms
            "orally": "by mouth",
            "sublingually": "under the tongue",
            "topically": "on the skin",
            "intramuscularly": "injected into muscle",
            "intravenously": "injected into vein",
            "subcutaneously": "injected under skin",
            "bid": "twice daily",
            "tid": "three times daily",
            "qid": "four times daily",
            "qd": "once daily",
            "prn": "as needed",
            "po": "by mouth",
            "mg": "milligrams",
            "mcg": "micrograms",
            "ml": "milliliters",
            "capsule": "pill",
            "tablet": "pill",
            
            # Medical conditions
            "hypertension": "high blood pressure",
            "diabetes mellitus": "diabetes",
            "gastroesophageal reflux": "acid reflux",
            "rhinitis": "runny nose",
            "conjunctivitis": "pink eye",
            "dermatitis": "skin inflammation",
            "arthritis": "joint inflammation",
            "bronchitis": "chest infection",
            "pneumonia": "lung infection",
            "gastritis": "stomach inflammation",
            "hepatitis": "liver inflammation",
            "nephritis": "kidney inflammation",
            
            # Pharmacological terms
            "bioavailability": "how much gets into your body",
            "half-life": "how long it stays in your body",
            "metabolism": "how your body processes it",
            "excretion": "how your body gets rid of it",
            "absorption": "how it gets into your body",
            "distribution": "how it spreads through your body",
            "therapeutic": "helpful for treatment",
            "prophylactic": "preventive",
            "analgesic": "pain reliever",
            "antipyretic": "fever reducer",
            "anti-inflammatory": "reduces swelling",
            "antihistamine": "allergy medicine",
            "antibiotic": "infection fighter",
            "antiviral": "virus fighter",
            "antifungal": "fungus fighter",
            "diuretic": "water pill",
            "laxative": "helps with bowel movements",
            "antiemetic": "prevents nausea",
            "sedative": "calming medicine",
            "stimulant": "energizing medicine",
            
            # Body systems
            "cardiovascular": "heart and blood vessels",
            "respiratory": "breathing system",
            "gastrointestinal": "stomach and intestines",
            "genitourinary": "urinary and reproductive systems",
            "musculoskeletal": "muscles and bones",
            "neurological": "nervous system",
            "dermatological": "skin-related",
            "ophthalmological": "eye-related",
            "otic": "ear-related",
            
            # Complex phrases
            "monitor hepatic function": "check liver health",
            "renal impairment": "kidney problems",
            "cardiac function": "heart health",
            "laboratory values": "blood test results",
            "clinical trials": "medical research studies",
            "placebo-controlled": "compared to fake medicine",
            "double-blind": "neither patient nor doctor knew which treatment",
            "randomized": "patients randomly assigned to treatments"
        }
        
        # Initialize LLM for complex translations
        self.llm = ChatOpenAI(
            model="gpt-3.5-turbo",  # Use cheaper model for translation
            temperature=0.1,
            api_key=settings.openai_api_key
        )
        
        # Translation prompt
        self.translation_prompt = ChatPromptTemplate.from_template("""
You are a medical translator that converts complex medical language into simple, plain English that anyone can understand.

RULES:
1. Use simple, everyday words
2. Explain medical terms in parentheses if needed
3. Keep the same meaning but make it accessible
4. Don't change dosages, drug names, or critical safety information
5. Use "you" instead of "patient"
6. Break up long sentences
7. Use bullet points for lists when helpful

EXAMPLES:
- "contraindication" → "reason you shouldn't take this"
- "hepatotoxicity" → "liver damage"
- "administered orally" → "taken by mouth"
- "monitor renal function" → "check your kidney health"

Medical text to translate:
{medical_text}

Plain English version:
""")
        
        # Create translation chain
        self.translation_chain = (
            self.translation_prompt
            | self.llm
            | StrOutputParser()
        )
    
    def translate_response(self, medical_response: str) -> str:
        """
        Translate a medical response into plain English
        
        Args:
            medical_response: Response containing medical jargon
            
        Returns:
            Plain English version of the response
        """
        try:
            # First, do quick dictionary replacements
            simplified = self._apply_dictionary_translations(medical_response)
            
            # If significant medical jargon remains, use LLM translation
            if self._contains_complex_medical_terms(simplified):
                # Use LLM for more sophisticated translation
                translated = self.translation_chain.invoke({"medical_text": simplified})
                return translated.strip()
            else:
                # Dictionary translations were sufficient
                return simplified
                
        except Exception as e:
            print(f"Translation error: {e}")
            # Fall back to dictionary-only translation
            return self._apply_dictionary_translations(medical_response)
    
    def _apply_dictionary_translations(self, text: str) -> str:
        """Apply dictionary-based translations"""
        # Create a case-insensitive replacement
        result = text
        
        # Sort by length (longest first) to avoid partial replacements
        sorted_terms = sorted(self.jargon_dict.items(), key=lambda x: len(x[0]), reverse=True)
        
        for jargon, plain in sorted_terms:
            # Use word boundaries to avoid partial matches
            pattern = r'\b' + re.escape(jargon) + r'\b'
            result = re.sub(pattern, plain, result, flags=re.IGNORECASE)
        
        return result
    
    def _contains_complex_medical_terms(self, text: str) -> bool:
        """Check if text still contains complex medical terminology"""
        # Patterns that suggest complex medical language
        complex_patterns = [
            r'\b\w+ology\b',  # -ology words
            r'\b\w+itis\b',   # -itis words
            r'\b\w+osis\b',   # -osis words
            r'\b\w+pathy\b',  # -pathy words
            r'\b\w+trophy\b', # -trophy words
            r'\b\w+genic\b',  # -genic words
            r'\b\w+static\b', # -static words
            r'\bmcg/kg\b',    # Complex dosing
            r'\bμg/ml\b',     # Greek letters
            r'\bCYP\d+\b',    # Enzyme names
        ]
        
        complex_word_count = 0
        for pattern in complex_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            complex_word_count += len(matches)
        
        # If more than 2 complex terms, use LLM translation
        return complex_word_count > 2
    
    def get_translation_preview(self, text: str) -> Dict[str, str]:
        """Get a preview of what would be translated"""
        translations = {}
        
        for jargon, plain in self.jargon_dict.items():
            pattern = r'\b' + re.escape(jargon) + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                translations[jargon] = plain
        
        return translations


# Example usage and testing
if __name__ == "__main__":
    translator = PlainEnglishTranslator()
    
    # Test with complex medical text
    test_text = """
    Contraindications include hypersensitivity to the active ingredient. 
    Monitor hepatic function during long-term administration. 
    Adverse effects may include hepatotoxicity, nephrotoxicity, and cardiovascular events including myocardial infarction.
    Administer orally bid with food to reduce gastrointestinal irritation.
    """
    
    print("Original:")
    print(test_text)
    print("\nTranslated:")
    print(translator.translate_response(test_text))
    
    print("\nDictionary translations found:")
    preview = translator.get_translation_preview(test_text)
    for jargon, plain in preview.items():
        print(f"  {jargon} → {plain}")