"""
RAG Pipeline for MedExplain
Combines retrieval from vector store with LLM generation for drug queries
"""

from typing import List, Dict, Any, Optional, Tuple
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import json

from .vectorstore import DrugVectorStore
from .safety import SafetyFilter, SafetyDisclaimer
from .dosage_advisor import DosageAdvisor
from .plain_english_translator import PlainEnglishTranslator
from .interaction_analyzer import InteractionAnalyzer
from .conversation_context import smart_detector
from ..utils.drug_normalizer import DrugNameNormalizer
from ..utils.multi_drug_parser import MultiDrugParser

# Import settings with fallback
try:
    from ...config.settings import settings
except ImportError:
    import sys
    from pathlib import Path
    config_path = Path(__file__).parent.parent.parent.parent / "config"
    sys.path.append(str(config_path))
    from settings import settings


class MedExplainRAG:
    """RAG pipeline for drug information queries"""
    
    def __init__(self):
        # Initialize components
        self.vector_store = DrugVectorStore()
        self.safety_filter = SafetyFilter()
        self.safety_disclaimer = SafetyDisclaimer()
        self.drug_normalizer = DrugNameNormalizer()
        self.dosage_advisor = DosageAdvisor()
        self.translator = PlainEnglishTranslator()
        self.multi_drug_parser = MultiDrugParser()
        self.interaction_analyzer = InteractionAnalyzer()
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=0.1,  # Low temperature for factual responses
            api_key=settings.openai_api_key
        )
        
        # Create the prompt template  
        self.prompt = ChatPromptTemplate.from_template("""
You are MedExplain, a friendly and helpful AI assistant that provides medication information in a conversational, user-friendly way.

RESPONSE STYLE:
- Be conversational, warm, and helpful (like talking to a knowledgeable friend)
- Give direct, clear answers without being overly formal
- Use "Yes" or "No" when appropriate instead of long disclaimers
- Make reasonable clinical assumptions based on available data
- NEVER start with "The FDA sources provided do not contain..." - instead make smart assumptions or give general guidance

SAFETY FIRST:
- Always include appropriate safety warnings
- Encourage consulting healthcare professionals for personalized advice
- Be clear about serious interactions or concerns

CONTEXT FROM MEDICAL SOURCES:
{context}

USER QUESTION: {question}

Provide a helpful, conversational response. If you don't have specific information, make reasonable assumptions based on drug classes and general medical knowledge, but always mention consulting a healthcare provider.

RESPONSE:
""")
        
        # Create the chain
        self.chain = (
            RunnablePassthrough.assign(context=self._retrieve_context)
            | self.prompt
            | self.llm
            | StrOutputParser()
        )
    
    def _retrieve_context(self, inputs: Dict[str, Any]) -> str:
        """Retrieve relevant context from vector store"""
        query = inputs["question"]
        
        # Search for relevant drug information (reduced for token limits)
        results = self.vector_store.search_drugs(query, n_results=3)
        
        if not results:
            return "No relevant FDA information found for this query."
        
        # Filter results by relevance threshold AND drug name matching
        relevant_results = []
        
        # Extract potential drug name from query for matching
        drug_name, _ = self.drug_normalizer.extract_and_normalize(query)
        
        for result in results:
            # Check if the result is actually relevant to the query
            distance = result.get("distance", 1.0)
            result_drug = result["metadata"].get("drug_name", "").lower()
            
            # Two conditions for relevance:
            # 1. Distance threshold for general similarity
            # 2. Drug name matching if we extracted a specific drug
            is_relevant = distance < 1.2
            
            if drug_name:
                # If we have a specific drug name, check for exact match
                drug_name_lower = drug_name.lower()
                is_drug_match = (
                    drug_name_lower in result_drug or 
                    result_drug in drug_name_lower or
                    drug_name_lower == result_drug
                )
                # For drug-specific queries, require both good similarity AND drug match
                is_relevant = distance < 1.5 and is_drug_match
            
            if is_relevant:
                relevant_results.append(result)
        
        if not relevant_results:
            print(f"🚫 No relevant results found for query: {query}")
            print(f"   Requested drug: {drug_name or 'unknown'}")
            print(f"   Best match: {results[0]['metadata'].get('drug_name', 'unknown')} (distance: {results[0].get('distance', 'unknown')})")
            return "No relevant FDA information found for this query."
        
        results = relevant_results
        
        # Format context
        context_parts = []
        for i, result in enumerate(results, 1):
            metadata = result["metadata"]
            document = result["document"]
            
            # Limit document length to prevent token overflow
            max_doc_length = 800  # Keep documents shorter
            truncated_doc = document[:max_doc_length]
            if len(document) > max_doc_length:
                truncated_doc += "...(truncated)"
            
            context_part = f"""
SOURCE {i}:
Drug: {metadata.get('drug_name', 'Unknown')}
Section: {metadata.get('section', 'Unknown').replace('_', ' ').title()}

Content:
{truncated_doc}
---
"""
            context_parts.append(context_part.strip())
        
        return "\n\n".join(context_parts)
    
    def query(self, question: str, include_safety_check: bool = True) -> Dict[str, Any]:
        """
        Process a user query and return response with metadata
        """
        # Safety check
        if include_safety_check:
            safety_result = self.safety_filter.check_query(question)
            if not safety_result["is_safe"]:
                return {
                    "response": safety_result["message"],
                    "safety_warning": True,
                    "confidence": "N/A",
                    "sources": [],
                    "disclaimer": self.safety_disclaimer.get_emergency_disclaimer()
                }
        
        # Check for drug interaction queries first with context awareness
        drug1, drug2 = smart_detector.detect_interaction_query(question)
        if drug1 and drug2:
            print(f"🔍 Detected interaction query: {drug1} + {drug2}")
            return self._handle_interaction_query(drug1, drug2, question)
        
        # Check for multi-drug queries
        if self.multi_drug_parser.is_multi_drug_query(question):
            print(f"🔍 Detected multi-drug query: {question[:100]}...")
            return self._handle_multi_drug_query(question)
        
        # Check for dosage-related queries (special handling required)
        if self.dosage_advisor.is_dosage_query(question):
            print(f"🔍 Detected dosage query: {question}")
            return self.dosage_advisor.handle_dosage_query(question)
        
        try:
            # Get retrieved context for source tracking
            context = self._retrieve_context({"question": question})
            
            # Check if we have relevant context
            if "No relevant FDA information found" in context:
                # Try to fetch the drug on-demand
                print(f"🔍 Drug not found in database, attempting to fetch: {question}")
                
                # Extract and normalize drug name from question
                drug_name, suggestions = self.drug_normalizer.extract_and_normalize(question)
                print(f"🎯 Extracted drug name: '{drug_name}', Suggestions: {suggestions}")
                
                if drug_name:
                    success = self._try_fetch_drug_on_demand(drug_name)
                    if success:
                        # Retry the search with newly added drug
                        print(f"🔄 Retrying search after adding {drug_name}")
                        context = self._retrieve_context({"question": question})
                        if "No relevant FDA information found" not in context:
                            print(f"✅ Successfully found {drug_name} data after fetch")
                            # Continue with normal processing
                        else:
                            print(f"❌ Still no data found for {drug_name}")
                            return self._no_drug_found_response(question, suggestions)
                    else:
                        print(f"❌ Failed to fetch {drug_name}")
                        return self._no_drug_found_response(question, suggestions)
                else:
                    print(f"❌ Could not extract drug name from: {question}")
                    return self._no_drug_found_response(question, [])
            
            # Generate response
            response = self.chain.invoke({"question": question})
            
            # Translate to plain English
            response = self.translator.translate_response(response)
            
            # Add drug to conversation context for future follow-up questions
            drug_name, _ = self.drug_normalizer.extract_and_normalize(question)
            if drug_name:
                smart_detector.add_drug_to_context(drug_name)
            
            # Extract sources from context
            sources = self._extract_sources_from_context(context)
            
            # Determine confidence based on source quality
            confidence = self._calculate_confidence(sources, context)
            
            # Get appropriate disclaimer
            disclaimer = self.safety_disclaimer.get_disclaimer_for_query(question)
            
            return {
                "response": response,
                "safety_warning": False,
                "confidence": confidence,
                "sources": sources,
                "disclaimer": disclaimer,
                "query": question
            }
            
        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error processing your question: {str(e)}",
                "safety_warning": False,
                "confidence": "Low",
                "sources": [],
                "disclaimer": self.safety_disclaimer.get_general_disclaimer(),
                "error": str(e)
            }
    
    def _extract_sources_from_context(self, context: str) -> List[Dict[str, str]]:
        """Extract source information from retrieved context"""
        sources = []
        
        # Parse context to extract source information
        context_sections = context.split("SOURCE ")
        for section in context_sections[1:]:  # Skip first empty split
            lines = section.split("\n")
            source_info = {}
            
            for line in lines:
                if line.startswith("Drug:"):
                    source_info["drug"] = line.replace("Drug:", "").strip()
                elif line.startswith("Section:"):
                    source_info["section"] = line.replace("Section:", "").strip()
                elif line.startswith("Source URL:"):
                    source_info["url"] = line.replace("Source URL:", "").strip()
                elif line.startswith("Last Updated:"):
                    source_info["last_updated"] = line.replace("Last Updated:", "").strip()
            
            if source_info:
                sources.append(source_info)
        
        return sources
    
    def _calculate_confidence(self, sources: List[Dict[str, str]], context: str) -> str:
        """Calculate confidence level based on source quality and content"""
        if not sources:
            return "Low"
        
        # High confidence: Multiple sources, recent updates, comprehensive content
        if len(sources) >= 3 and len(context) > 500:
            return "High"
        elif len(sources) >= 2 and len(context) > 200:
            return "Medium"
        else:
            return "Low"
    
    def get_drug_overview(self, drug_name: str) -> Dict[str, Any]:
        """Get comprehensive overview of a specific drug"""
        # Get all sections for the drug
        drug_results = self.vector_store.get_drug_by_name(drug_name)
        
        if not drug_results:
            return {
                "drug_name": drug_name,
                "found": False,
                "message": f"No FDA information found for '{drug_name}'. Please check the spelling or try a different name."
            }
        
        # Organize by sections
        sections = {}
        metadata = {}
        
        for result in drug_results:
            section = result["metadata"]["section"]
            sections[section] = result["document"]
            if not metadata:  # Get metadata from first result
                metadata = result["metadata"]
        
        # Convert brand_names back to list if it's a string
        brand_names = metadata.get("brand_names", "")
        if isinstance(brand_names, str):
            brand_names = [name.strip() for name in brand_names.split(",") if name.strip()]
        
        return {
            "drug_name": drug_name,
            "found": True,
            "generic_name": metadata.get("generic_name"),
            "brand_names": brand_names,
            "sections": sections,
            "source_url": metadata.get("source_url"),
            "last_updated": metadata.get("last_updated"),
            "disclaimer": self.safety_disclaimer.get_general_disclaimer()
        }
    
    def suggest_drugs(self, partial_name: str, limit: int = 5) -> List[str]:
        """Suggest drug names based on partial input"""
        all_drugs = self.vector_store.list_all_drugs()
        
        # Simple substring matching (can be improved with fuzzy matching)
        suggestions = [
            drug for drug in all_drugs 
            if partial_name.lower() in drug.lower()
        ]
        
        return suggestions[:limit]
    
    def _extract_drug_name(self, question: str) -> str:
        """Extract potential drug name from user question"""
        import re
        
        # Common patterns to extract drug names
        patterns = [
            r"(?:about|of|is|tell me about|what is)\s+([A-Za-z]+)",
            r"([A-Za-z]+)\s+(?:side effects|uses|dosage|contraindications)",
            r"(?:what does|what is)\s+([A-Za-z]+)",
            r"(?:does|do)\s+([A-Za-z]+)\s+(?:do|does|work)",
            r"\b([A-Za-z]{4,})\b",  # Any word 4+ characters (likely drug name)
        ]
        
        # Common words to exclude
        exclude_words = {
            'what', 'does', 'the', 'side', 'effects', 'uses', 'about', 'is', 'are',
            'tell', 'me', 'how', 'can', 'will', 'should', 'would', 'could', 'have',
            'that', 'this', 'they', 'them', 'with', 'from', 'take', 'taking',
            'medication', 'medicine', 'drug', 'pill', 'tablet'
        }
        
        for pattern in patterns:
            matches = re.findall(pattern, question, re.IGNORECASE)
            for match in matches:
                potential_drug = match.strip()
                if potential_drug.lower() not in exclude_words and len(potential_drug) >= 4:
                    return potential_drug.title()
        
        return ""
    
    def _try_fetch_drug_on_demand(self, drug_name: str) -> bool:
        """Try to fetch and add a drug to the database on-demand"""
        try:
            from ..data.fda_fetcher import FDAFetcher
            
            print(f"  📡 Fetching {drug_name} from multiple sources...")
            # Enable enhanced sources for more comprehensive data
            fetcher = FDAFetcher(use_enhanced_sources=True)
            drug_info = fetcher.get_drug_info(drug_name)
            
            if drug_info:
                success = self.vector_store.add_drug(drug_info)
                if success:
                    print(f"  ✅ Successfully added {drug_name} to database")
                    return True
                else:
                    print(f"  ❌ Failed to add {drug_name} to database")
            else:
                print(f"  ⚠️  No FDA data found for {drug_name}")
            
            return False
            
        except Exception as e:
            print(f"  ❌ Error fetching {drug_name}: {e}")
            return False
    
    def _no_drug_found_response(self, question: str, suggestions: List[str] = None) -> Dict[str, Any]:
        """Generate response when drug is not found"""
        all_drugs = self.vector_store.list_all_drugs()
        suggestion_msg = f"I don't have information about this specific medication in my current database. "
        
        # Add smart suggestions if available
        if suggestions:
            suggestion_msg += f"\n\n🤔 **Did you mean one of these?**\n"
            for i, suggestion in enumerate(suggestions[:3], 1):
                suggestion_msg += f"{i}. {suggestion}\n"
            suggestion_msg += "\nYou can ask about any of these instead."
        
        if all_drugs:
            suggestion_msg += f"\n\n📋 **I currently have information about these medications:**\n{', '.join(all_drugs[:10])}."
            if len(all_drugs) > 10:
                suggestion_msg += f"\n(and {len(all_drugs) - 10} more...)"
            suggestion_msg += "\n\nYou can ask about any of these, or contact your healthcare provider for information about other medications."
        else:
            suggestion_msg += "\n\nPlease consult your healthcare provider or pharmacist for accurate information about this medication."
        
        return {
            "response": suggestion_msg,
            "safety_warning": False,
            "confidence": "Low", 
            "sources": [],
            "disclaimer": self.safety_disclaimer.get_general_disclaimer(),
            "query": question
        }
    
    def _handle_interaction_query(self, drug1: str, drug2: str, original_question: str) -> Dict[str, Any]:
        """Handle drug interaction queries with smart assumptions"""
        try:
            # Use interaction analyzer for smart assumptions
            interaction_result = self.interaction_analyzer.analyze_interaction(drug1, drug2)
            
            # Create user-friendly response
            response = interaction_result['description']
            
            # Add practical advice
            if interaction_result['advice']:
                response += f"\n\n💡 **Practical advice:** {interaction_result['advice']}"
            
            # Add general safety reminder
            response += f"\n\n🏥 **Remember:** Always inform your doctor and pharmacist about all medications you're taking, including over-the-counter drugs and supplements."
            
            # Translate to plain English
            response = self.translator.translate_response(response)
            
            return {
                "response": response,
                "safety_warning": interaction_result['severity'] in ['caution', 'monitor'],
                "confidence": interaction_result['confidence'],
                "sources": [
                    {"drug": drug1, "section": "Drug Interaction Analysis", "url": "Clinical Database"},
                    {"drug": drug2, "section": "Drug Interaction Analysis", "url": "Clinical Database"}
                ],
                "disclaimer": "This interaction analysis is based on general medical knowledge and drug classification patterns. Individual responses may vary.",
                "query": original_question
            }
            
        except Exception as e:
            print(f"❌ Error in interaction analysis: {e}")
            # Fallback to basic response
            return {
                "response": f"I can help you check if {drug1} and {drug2} can be taken together. Let me consult my healthcare provider for the most accurate information about combining these specific medications.",
                "safety_warning": True,
                "confidence": "Low",
                "sources": [],
                "disclaimer": "Always consult your healthcare provider before combining medications.",
                "query": original_question
            }
    
    def _handle_multi_drug_query(self, question: str) -> Dict[str, Any]:
        """Handle queries containing multiple drug names"""
        try:
            # Extract individual drug names
            drugs = self.multi_drug_parser.extract_drug_list(question)
            print(f"🎯 Extracted {len(drugs)} drugs: {drugs}")
            
            if not drugs:
                return self._no_drug_found_response(question, [])
            
            # Limit to prevent excessive API calls
            max_drugs = 10
            if len(drugs) > max_drugs:
                drugs = drugs[:max_drugs]
                print(f"⚠️ Limited to first {max_drugs} drugs to manage costs")
            
            # Create individual queries
            individual_queries = self.multi_drug_parser.create_individual_queries(drugs, question)
            
            # Process each drug individually
            drug_responses = []
            for i, (drug, individual_query) in enumerate(zip(drugs, individual_queries)):
                print(f"📋 Processing {i+1}/{len(drugs)}: {drug}")
                
                # Query each drug individually (without multi-drug detection to avoid recursion)
                response = self._query_single_drug(individual_query)
                response['drug_name'] = drug
                drug_responses.append(response)
            
            # Combine responses
            combined_response = self.multi_drug_parser.format_combined_response(drug_responses, question)
            
            print(f"✅ Successfully processed {len(drug_responses)} drugs")
            return combined_response
            
        except Exception as e:
            print(f"❌ Error processing multi-drug query: {e}")
            return {
                "response": f"I encountered an error processing your multi-drug query: {str(e)}",
                "safety_warning": False,
                "confidence": "Low",
                "sources": [],
                "disclaimer": self.safety_disclaimer.get_general_disclaimer(),
                "error": str(e)
            }
    
    def _query_single_drug(self, question: str) -> Dict[str, Any]:
        """Process a single drug query without multi-drug detection"""
        try:
            # Check for dosage-related queries
            if self.dosage_advisor.is_dosage_query(question):
                return self.dosage_advisor.handle_dosage_query(question)
            
            # Get retrieved context for source tracking
            context = self._retrieve_context({"question": question})
            
            # Check if we have relevant context
            if "No relevant FDA information found" in context:
                # Try to fetch the drug on-demand
                drug_name, suggestions = self.drug_normalizer.extract_and_normalize(question)
                
                if drug_name:
                    success = self._try_fetch_drug_on_demand(drug_name)
                    if success:
                        context = self._retrieve_context({"question": question})
                        if "No relevant FDA information found" not in context:
                            # Continue with normal processing
                            pass
                        else:
                            return self._no_drug_found_response(question, suggestions)
                    else:
                        return self._no_drug_found_response(question, suggestions)
                else:
                    return self._no_drug_found_response(question, [])
            
            # Generate response
            response = self.chain.invoke({"question": question})
            
            # Translate to plain English
            response = self.translator.translate_response(response)
            
            # Add drug to conversation context for future follow-up questions
            drug_name, _ = self.drug_normalizer.extract_and_normalize(question)
            if drug_name:
                smart_detector.add_drug_to_context(drug_name)
            
            # Extract sources from context
            sources = self._extract_sources_from_context(context)
            
            # Determine confidence based on source quality
            confidence = self._calculate_confidence(sources, context)
            
            # Get appropriate disclaimer
            disclaimer = self.safety_disclaimer.get_disclaimer_for_query(question)
            
            return {
                "response": response,
                "safety_warning": False,
                "confidence": confidence,
                "sources": sources,
                "disclaimer": disclaimer,
                "query": question
            }
            
        except Exception as e:
            return {
                "response": f"I apologize, but I encountered an error processing your question: {str(e)}",
                "safety_warning": False,
                "confidence": "Low",
                "sources": [],
                "disclaimer": self.safety_disclaimer.get_general_disclaimer(),
                "error": str(e)
            }


# Example usage and testing
if __name__ == "__main__":
    # Initialize RAG pipeline
    rag = MedExplainRAG()
    
    # Test queries
    test_queries = [
        "What are the side effects of ibuprofen?",
        "How much acetaminophen should I take?",  # Should trigger safety warning
        "What is lisinopril used for?",
        "Tell me about metformin contraindications"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        
        result = rag.query(query)
        
        print(f"Response: {result['response']}")
        print(f"Confidence: {result['confidence']}")
        print(f"Safety Warning: {result['safety_warning']}")
        
        if result['sources']:
            print("Sources:")
            for source in result['sources']:
                print(f"  - {source.get('drug', 'Unknown')} ({source.get('section', 'Unknown')})")
        
        print(f"Disclaimer: {result['disclaimer']}")
        print("=" * 50)