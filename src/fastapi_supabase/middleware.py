# middleware.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from .config import SupabaseAuthConfig

def add_cors_middleware(app: FastAPI, config: SupabaseAuthConfig):
    """
    Adds CORS middleware to the FastAPI app using the provided configuration.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.origins,  # Use origins from config
        allow_credentials=True,
        allow_methods=["*"],  # Allows all HTTP methods
        allow_headers=["*"],  # Allows all headers
    )
