"""
Drug Interaction Analyzer for MedExplain
Makes smart assumptions about drug interactions based on drug classes and known patterns
"""

from typing import Dict, List, Optional, Tuple
import re


class InteractionAnalyzer:
    """Analyzes drug interactions and makes smart clinical assumptions"""
    
    def __init__(self):
        # Common safe combinations (low interaction risk)
        self.safe_combinations = {
            # Pain relievers with antibiotics
            ('acetaminophen', 'amoxicillin'): 'safe',
            ('acetaminophen', 'azithromycin'): 'safe',
            ('acetaminophen', 'cephalexin'): 'safe',
            ('ibuprofen', 'amoxicillin'): 'safe_with_caution',
            
            # Common pain relievers together (with warnings)  
            ('acetaminophen', 'ibuprofen'): 'safe_alternating',
            
            # Heart medications with antibiotics
            ('lisinopril', 'amoxicillin'): 'safe',
            ('amlodipine', 'amoxicillin'): 'safe',
            ('metoprolol', 'amoxicillin'): 'safe',
            
            # Diabetes medications with antibiotics
            ('metformin', 'amoxicillin'): 'safe',
            ('metformin', 'azithromycin'): 'safe',
        }
        
        # Known problematic combinations
        self.problematic_combinations = {
            # Blood thinners with NSAIDs
            ('warfarin', 'ibuprofen'): 'bleeding_risk',
            ('warfarin', 'aspirin'): 'bleeding_risk',
            ('warfarin', 'naproxen'): 'bleeding_risk',
            
            # Multiple NSAIDs
            ('ibuprofen', 'naproxen'): 'increased_side_effects',
            ('ibuprofen', 'aspirin'): 'increased_bleeding_gi_risk',
            
            # Sedating medications
            ('zolpidem', 'lorazepam'): 'excessive_sedation',
            ('alprazolam', 'zolpidem'): 'excessive_sedation',
        }
        
        # Drug class interaction patterns
        self.class_interactions = {
            ('nsaid', 'ace_inhibitor'): 'reduced_effectiveness',
            ('nsaid', 'diuretic'): 'kidney_function_concern',
            ('beta_blocker', 'calcium_channel_blocker'): 'low_blood_pressure_risk',
            ('ssri', 'nsaid'): 'bleeding_risk',
        }
        
        # Drug class mappings
        self.drug_classes = {
            'acetaminophen': 'analgesic',
            'ibuprofen': 'nsaid',
            'naproxen': 'nsaid',
            'aspirin': 'nsaid',
            'lisinopril': 'ace_inhibitor',
            'amlodipine': 'calcium_channel_blocker',
            'metoprolol': 'beta_blocker',
            'hydrochlorothiazide': 'diuretic',
            'sertraline': 'ssri',
            'fluoxetine': 'ssri',
            'warfarin': 'anticoagulant',
            'amoxicillin': 'antibiotic',
            'azithromycin': 'antibiotic',
            'cephalexin': 'antibiotic',
        }
    
    def analyze_interaction(self, drug1: str, drug2: str) -> Dict[str, any]:
        """Analyze interaction between two drugs"""
        drug1_lower = drug1.lower().strip()
        drug2_lower = drug2.lower().strip()
        
        # Normalize drug names (handle common variants)
        drug1_normalized = self._normalize_drug_name(drug1_lower)
        drug2_normalized = self._normalize_drug_name(drug2_lower)
        
        # Check both orderings
        combination1 = (drug1_normalized, drug2_normalized)
        combination2 = (drug2_normalized, drug1_normalized)
        
        # Check safe combinations first
        if combination1 in self.safe_combinations:
            return self._create_interaction_response(
                drug1, drug2, self.safe_combinations[combination1], 'safe'
            )
        elif combination2 in self.safe_combinations:
            return self._create_interaction_response(
                drug1, drug2, self.safe_combinations[combination2], 'safe'
            )
        
        # Check problematic combinations
        if combination1 in self.problematic_combinations:
            return self._create_interaction_response(
                drug1, drug2, self.problematic_combinations[combination1], 'caution'
            )
        elif combination2 in self.problematic_combinations:
            return self._create_interaction_response(
                drug1, drug2, self.problematic_combinations[combination2], 'caution'
            )
        
        # Check by drug class
        class1 = self.drug_classes.get(drug1_normalized)
        class2 = self.drug_classes.get(drug2_normalized)
        
        if class1 and class2:
            class_combo1 = (class1, class2)
            class_combo2 = (class2, class1)
            
            if class_combo1 in self.class_interactions:
                return self._create_interaction_response(
                    drug1, drug2, self.class_interactions[class_combo1], 'monitor'
                )
            elif class_combo2 in self.class_interactions:
                return self._create_interaction_response(
                    drug1, drug2, self.class_interactions[class_combo2], 'monitor'
                )
        
        # Default response for unknown combinations
        return self._create_unknown_interaction_response(drug1, drug2)
    
    def _normalize_drug_name(self, drug_name: str) -> str:
        """Normalize drug name to standard form"""
        # Handle common variants
        variants = {
            'tylenol': 'acetaminophen',
            'advil': 'ibuprofen',
            'motrin': 'ibuprofen',
            'aleve': 'naproxen',
            'zpack': 'azithromycin',
            'amoxil': 'amoxicillin',
        }
        return variants.get(drug_name, drug_name)
    
    def _create_interaction_response(self, drug1: str, drug2: str, interaction_type: str, severity: str) -> Dict[str, any]:
        """Create a structured interaction response"""
        responses = {
            'safe': f"Yes, {drug1} and {drug2} are generally safe to take together. There are no known significant interactions between these medications.",
            
            'safe_with_caution': f"Yes, {drug1} and {drug2} can typically be taken together, but monitor for increased side effects. Take the anti-inflammatory with food to reduce stomach irritation.",
            
            'safe_alternating': f"Yes, {drug1} and {drug2} can be taken together and are sometimes recommended in alternating doses for better pain control. Space them out by 2-3 hours when possible.",
            
            'bleeding_risk': f"⚠️ **Caution needed.** {drug1} and {drug2} can increase bleeding risk when taken together. Your doctor may need to monitor you more closely or adjust dosages.",
            
            'increased_side_effects': f"⚠️ **Not recommended.** Taking {drug1} and {drug2} together can increase the risk of side effects like stomach problems and kidney issues. Choose one or consult your doctor.",
            
            'increased_bleeding_gi_risk': f"⚠️ **Caution needed.** {drug1} and {drug2} together increase the risk of stomach bleeding and ulcers. Take with food and watch for stomach pain.",
            
            'excessive_sedation': f"⚠️ **Not recommended without medical supervision.** {drug1} and {drug2} can cause dangerous levels of sedation and breathing problems when combined.",
            
            'reduced_effectiveness': f"⚠️ **Monitor closely.** {drug1} may reduce the effectiveness of {drug2}. Your doctor might need to adjust dosages or monitor your response.",
            
            'kidney_function_concern': f"⚠️ **Monitor kidney function.** This combination can affect kidney function, especially if you're dehydrated or elderly. Drink plenty of water.",
            
            'low_blood_pressure_risk': f"⚠️ **Monitor blood pressure.** This combination can cause blood pressure to drop too low. Watch for dizziness or lightheadedness.",
        }
        
        advice = {
            'safe': "You can take these medications as directed by your doctor or the package instructions.",
            'caution': "Consult your doctor or pharmacist before combining these medications, especially if you have other health conditions.",
            'monitor': "Regular monitoring may be needed when taking these together. Keep track of any new symptoms."
        }
        
        return {
            'interaction_found': True,
            'severity': severity,
            'description': responses.get(interaction_type, "Interaction noted"),
            'advice': advice.get(severity, "Consult your healthcare provider"),
            'confidence': 'High' if interaction_type in ['safe', 'bleeding_risk'] else 'Moderate'
        }
    
    def _create_unknown_interaction_response(self, drug1: str, drug2: str) -> Dict[str, any]:
        """Create response for unknown drug combinations"""
        return {
            'interaction_found': False,
            'severity': 'unknown',
            'description': f"No specific interaction information is available for {drug1} and {drug2} in my current database. However, this doesn't mean they're automatically safe together.",
            'advice': "Always consult with your doctor or pharmacist before combining medications, even if no interactions are known. They can review your complete medication list and health history.",
            'confidence': 'Low'
        }


def detect_interaction_query(query: str) -> Tuple[Optional[str], Optional[str]]:
    """Detect if query is asking about drug interactions and extract drug names"""
    interaction_patterns = [
        r"can i take (.+?) with (.+?)\?",
        r"(.+?) and (.+?) together",
        r"(.+?) with (.+?) interaction",
        r"combining (.+?) and (.+?)",
        r"take (.+?) and (.+?)",
        r"(.+?) and (.+?) safe",
    ]
    
    query_lower = query.lower().strip()
    
    for pattern in interaction_patterns:
        match = re.search(pattern, query_lower)
        if match:
            drug1 = match.group(1).strip()
            drug2 = match.group(2).strip()
            
            # Clean up common noise words
            noise_words = ['the', 'a', 'an', 'my', 'some', 'any']
            drug1 = ' '.join([word for word in drug1.split() if word not in noise_words])
            drug2 = ' '.join([word for word in drug2.split() if word not in noise_words])
            
            if drug1 and drug2 and len(drug1) > 2 and len(drug2) > 2:
                return drug1.title(), drug2.title()
    
    return None, None


# Example usage
if __name__ == "__main__":
    analyzer = InteractionAnalyzer()
    
    test_queries = [
        "Can I take Acetaminophen with Amoxicillin?",
        "Is it safe to take Ibuprofen and Warfarin together?",
        "Can I combine Tylenol and Advil?",
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        drug1, drug2 = detect_interaction_query(query)
        
        if drug1 and drug2:
            result = analyzer.analyze_interaction(drug1, drug2)
            print(f"Drugs: {drug1} + {drug2}")
            print(f"Severity: {result['severity']}")
            print(f"Response: {result['description']}")
        else:
            print("No interaction query detected")