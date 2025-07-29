"""
Database Setup Script for MedExplain
Run this script to initialize and seed the vector database with FDA drug data
"""

import sys
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.medexplain.core.vectorstore import DrugVectorStore
from src.medexplain.data.fda_fetcher import FDAFetcher


def main():
    """Set up and seed the database"""
    print("🚀 Starting MedExplain Database Setup")
    print("=" * 50)
    
    # Check if required environment variables are set
    required_vars = ["OPENAI_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease create a .env file with the required variables.")
        print("See .env.example for reference.")
        return
    
    print("✅ Environment variables loaded")
    
    # Initialize vector store
    print("\n📚 Initializing vector database...")
    try:
        vector_store = DrugVectorStore()
        print("✅ Vector database initialized")
    except Exception as e:
        print(f"❌ Error initializing vector database: {e}")
        return
    
    # Check current status
    stats = vector_store.get_collection_stats()
    current_drugs = stats.get("total_drugs", 0)
    current_docs = stats.get("total_documents", 0)
    
    print(f"\n📊 Current database status:")
    print(f"   - Drugs: {current_drugs}")
    print(f"   - Documents: {current_docs}")
    
    if current_drugs > 0:
        response = input(f"\nDatabase already has {current_drugs} drugs. Add more? (y/n): ")
        if response.lower() != 'y':
            print("✅ Setup complete!")
            return
    
    # Ask how many drugs to add
    try:
        limit = int(input(f"\nHow many drugs to add? (recommended: 10-25): ") or "10")
    except ValueError:
        limit = 10
    
    print(f"\n🔄 Seeding database with {limit} drugs...")
    print("This may take a few minutes due to API rate limiting...")
    
    try:
        success_count = vector_store.seed_database(limit=limit)
        print(f"\n✅ Successfully added {success_count}/{limit} drugs to database")
    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        return
    
    # Final stats
    final_stats = vector_store.get_collection_stats()
    final_drugs = final_stats.get("total_drugs", 0)
    final_docs = final_stats.get("total_documents", 0)
    
    print(f"\n🎉 Database setup complete!")
    print(f"   - Total drugs: {final_drugs}")
    print(f"   - Total documents: {final_docs}")
    
    if final_stats.get("drugs"):
        print(f"\n📋 Available drugs (sample):")
        for drug in final_stats["drugs"][:10]:
            print(f"   • {drug}")
    
    print(f"\n🚀 Ready to run MedExplain!")
    print(f"   Run: streamlit run app.py")


if __name__ == "__main__":
    main()