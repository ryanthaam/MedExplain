"""
Vector Store Manager for MedExplain
Handles ChromaDB operations for drug information storage and retrieval
"""

import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
import hashlib
import json
from pathlib import Path

from ..data.fda_fetcher import DrugInfo, FDAFetcher

# Import settings with fallback
try:
    from ...config.settings import settings
except ImportError:
    import sys
    from pathlib import Path
    config_path = Path(__file__).parent.parent.parent.parent / "config"
    sys.path.append(str(config_path))
    from settings import settings


class DrugVectorStore:
    """Manages drug information in ChromaDB vector database"""
    
    def __init__(self, persist_directory: str = None):
        self.persist_directory = persist_directory or settings.vector_db_path
        Path(self.persist_directory).mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=self.persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="drug_information",
            metadata={"description": "FDA drug information for MedExplain"}
        )
    
    def _create_document_id(self, drug_name: str, section: str) -> str:
        """Create unique document ID"""
        content = f"{drug_name.lower()}_{section}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _prepare_drug_documents(self, drug_info: DrugInfo) -> List[Dict[str, Any]]:
        """
        Convert DrugInfo into documents for vector storage
        Each section becomes a separate document for better retrieval
        """
        documents = []
        
        sections = {
            "description": drug_info.description,
            "indications": drug_info.indications,
            "contraindications": drug_info.contraindications,
            "warnings": drug_info.warnings,
            "adverse_reactions": drug_info.adverse_reactions,
            "dosage": drug_info.dosage
        }
        
        for section_name, content in sections.items():
            if content and content.strip():
                doc_id = self._create_document_id(drug_info.name, section_name)
                
                # Create searchable text combining drug names and content
                searchable_text = f"""
                Drug Name: {drug_info.name}
                Generic Name: {drug_info.generic_name or 'N/A'}
                Brand Names: {', '.join(drug_info.brand_names)}
                Section: {section_name.replace('_', ' ').title()}
                
                {content}
                """
                
                documents.append({
                    "id": doc_id,
                    "document": searchable_text.strip(),
                    "metadata": {
                        "drug_name": drug_info.name,
                        "generic_name": drug_info.generic_name or "",
                        "brand_names": ", ".join(drug_info.brand_names) if drug_info.brand_names else "",
                        "section": section_name,
                        "source_url": drug_info.source_url,
                        "last_updated": drug_info.last_updated,
                        "ndc_codes": ", ".join(drug_info.ndc_codes) if drug_info.ndc_codes else ""
                    }
                })
        
        return documents
    
    def add_drug(self, drug_info: DrugInfo) -> bool:
        """Add a drug to the vector store"""
        try:
            documents = self._prepare_drug_documents(drug_info)
            
            if not documents:
                print(f"No content to add for drug: {drug_info.name}")
                return False
            
            # Extract data for ChromaDB
            ids = [doc["id"] for doc in documents]
            docs = [doc["document"] for doc in documents]
            metadatas = [doc["metadata"] for doc in documents]
            
            # Add to collection
            self.collection.add(
                documents=docs,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"Added {len(documents)} documents for drug: {drug_info.name}")
            return True
            
        except Exception as e:
            print(f"Error adding drug {drug_info.name}: {e}")
            return False
    
    def search_drugs(self, query: str, n_results: int = 5) -> List[Dict[str, Any]]:
        """Search for drug information using vector similarity"""
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            # Format results
            formatted_results = []
            if results['documents'] and results['documents'][0]:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        "document": results['documents'][0][i],
                        "metadata": results['metadatas'][0][i],
                        "distance": results['distances'][0][i] if results['distances'] else None
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching drugs: {e}")
            return []
    
    def get_drug_by_name(self, drug_name: str) -> List[Dict[str, Any]]:
        """Get all information for a specific drug"""
        try:
            # Search for exact drug name match
            results = self.collection.get(
                where={"drug_name": {"$eq": drug_name}},
                include=["documents", "metadatas"]
            )
            
            formatted_results = []
            if results['documents']:
                for i in range(len(results['documents'])):
                    formatted_results.append({
                        "document": results['documents'][i],
                        "metadata": results['metadatas'][i]
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error getting drug {drug_name}: {e}")
            return []
    
    def list_all_drugs(self) -> List[str]:
        """Get list of all drugs in the database"""
        try:
            # Get all unique drug names
            results = self.collection.get(include=["metadatas"])
            drug_names = set()
            
            for metadata in results['metadatas']:
                if 'drug_name' in metadata:
                    drug_names.add(metadata['drug_name'])
            
            return sorted(list(drug_names))
            
        except Exception as e:
            print(f"Error listing drugs: {e}")
            return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection"""
        try:
            count = self.collection.count()
            drugs = self.list_all_drugs()
            
            return {
                "total_documents": count,
                "total_drugs": len(drugs),
                "drugs": drugs[:10],  # First 10 for preview
                "collection_name": self.collection.name
            }
            
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {}
    
    def seed_database(self, limit: int = 25):
        """Seed the database with popular drugs"""
        fetcher = FDAFetcher()
        popular_drugs = fetcher.get_popular_drugs(limit)
        
        print(f"Seeding database with {len(popular_drugs)} drugs...")
        
        success_count = 0
        for drug_name in popular_drugs:
            try:
                print(f"Processing: {drug_name}")
                drug_info = fetcher.get_drug_info(drug_name)
                
                if drug_info:
                    if self.add_drug(drug_info):
                        success_count += 1
                    else:
                        print(f"Failed to add {drug_name} to database")
                else:
                    print(f"No information found for {drug_name}")
                
                # Rate limiting
                import time
                time.sleep(1)
                
            except Exception as e:
                print(f"Error processing {drug_name}: {e}")
        
        print(f"Successfully added {success_count}/{len(popular_drugs)} drugs to database")
        return success_count


# Example usage
if __name__ == "__main__":
    # Initialize vector store
    store = DrugVectorStore()
    
    # Get stats
    stats = store.get_collection_stats()
    print("Database stats:", stats)
    
    # If empty, seed the database
    if stats.get("total_drugs", 0) == 0:
        store.seed_database(limit=5)  # Start with 5 drugs for testing
    
    # Test search
    results = store.search_drugs("What are the side effects of ibuprofen?")
    for result in results:
        print(f"Drug: {result['metadata']['drug_name']}")
        print(f"Section: {result['metadata']['section']}")
        print(f"Content: {result['document'][:200]}...")
        print("---")