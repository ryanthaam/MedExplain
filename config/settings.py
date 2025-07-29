"""
Configuration settings for MedExplain application
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings using Pydantic for environment variable management"""
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4"
    openai_embedding_model: str = "text-embedding-3-large"
    
    # Supabase Configuration (Disabled for MVP)
    # supabase_url: Optional[str] = None
    # supabase_anon_key: Optional[str] = None
    # supabase_service_key: Optional[str] = None
    
    # LangSmith Configuration (Optional)
    langchain_tracing_v2: bool = True
    langchain_api_key: Optional[str] = None
    langchain_project: str = "medexplain"
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # FDA API Configuration
    fda_api_key: Optional[str] = None
    
    # Security
    secret_key: str
    
    # Vector Database
    vector_db_path: str = "./chroma_db"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()