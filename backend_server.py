"""
FastAPI Backend Server for MedExplain React Frontend
Provides REST API endpoints for the React app to interact with MedExplain backend
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
import sys
from pathlib import Path

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from medexplain.core.rag_pipeline import MedExplainRAG

app = FastAPI(
    title="MedExplain API",
    description="AI-powered medication information from FDA sources",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG pipeline
rag_pipeline = None

@app.on_event("startup")
async def startup_event():
    global rag_pipeline
    try:
        rag_pipeline = MedExplainRAG()
        print("✅ MedExplain RAG pipeline initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize RAG pipeline: {e}")
        raise e

# Request/Response Models
class QueryRequest(BaseModel):
    question: str
    include_safety_check: bool = True

class DrugSource(BaseModel):
    drug: str
    section: str
    url: Optional[str] = None
    last_updated: Optional[str] = None

class QueryResponse(BaseModel):
    response: str
    safety_warning: bool
    confidence: str
    sources: List[DrugSource]
    disclaimer: str
    query: str
    multi_drug_count: Optional[int] = None
    error: Optional[str] = None

class SuggestionsResponse(BaseModel):
    suggestions: List[str]

class DrugsListResponse(BaseModel):
    drugs: List[str]

# API Endpoints
@app.get("/")
async def root():
    return {"message": "MedExplain API is running", "status": "healthy"}

@app.post("/query", response_model=QueryResponse)
async def query_drug(request: QueryRequest):
    """Query drug information"""
    if not rag_pipeline:
        raise HTTPException(status_code=500, detail="RAG pipeline not initialized")
    
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    
    try:
        result = rag_pipeline.query(
            question=request.question.strip(),
            include_safety_check=request.include_safety_check
        )
        
        # Convert sources to match frontend model
        sources = []
        for source in result.get('sources', []):
            sources.append(DrugSource(
                drug=source.get('drug', ''),
                section=source.get('section', ''),
                url=source.get('url'),
                last_updated=source.get('last_updated')
            ))
        
        return QueryResponse(
            response=result['response'],
            safety_warning=result.get('safety_warning', False),
            confidence=result.get('confidence', 'Low'),
            sources=sources,
            disclaimer=result.get('disclaimer', ''),
            query=result.get('query', request.question),
            multi_drug_count=result.get('multi_drug_count'),
            error=result.get('error')
        )
        
    except Exception as e:
        print(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/drug/{drug_name}")
async def get_drug_overview(drug_name: str):
    """Get comprehensive overview of a specific drug"""
    if not rag_pipeline:
        raise HTTPException(status_code=500, detail="RAG pipeline not initialized")
    
    try:
        result = rag_pipeline.get_drug_overview(drug_name)
        return result
    except Exception as e:
        print(f"Error getting drug overview: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/suggest", response_model=SuggestionsResponse)
async def suggest_drugs(partial_name: str, limit: int = 5):
    """Get drug name suggestions based on partial input"""
    if not rag_pipeline:
        raise HTTPException(status_code=500, detail="RAG pipeline not initialized")
    
    try:
        suggestions = rag_pipeline.suggest_drugs(partial_name, limit)
        return SuggestionsResponse(suggestions=suggestions)
    except Exception as e:
        print(f"Error getting suggestions: {e}")
        return SuggestionsResponse(suggestions=[])

@app.get("/drugs", response_model=DrugsListResponse)
async def list_all_drugs():
    """List all available drugs in the database"""
    if not rag_pipeline:
        raise HTTPException(status_code=500, detail="RAG pipeline not initialized")
    
    try:
        drugs = rag_pipeline.vector_store.list_all_drugs()
        return DrugsListResponse(drugs=drugs)
    except Exception as e:
        print(f"Error listing drugs: {e}")
        return DrugsListResponse(drugs=[])

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "rag_initialized": rag_pipeline is not None,
        "message": "MedExplain API is operational"
    }

if __name__ == "__main__":
    print("🚀 Starting MedExplain FastAPI server...")
    print("📚 Frontend will be available at: http://localhost:3000")
    print("🔗 API docs available at: http://localhost:8000/docs")
    
    uvicorn.run(
        "backend_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )