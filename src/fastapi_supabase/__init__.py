"""
FastAPI Supabase - A lightweight authentication integration for FastAPI and Supabase
"""
from fastapi_supabase.config import SupabaseAuthConfig
from fastapi_supabase.auth import JWTAuthenticator
from fastapi_supabase.middleware import add_cors_middleware

__version__ = "0.1.0"
__all__ = ["SupabaseAuthConfig", "JWTAuthenticator", "add_cors_middleware"]