# middleware.py
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
import config

def add_cors_middleware(app: FastAPI):

    # hardcoded ?
    # origins = [
    # ]

    origins =  config.ORIGINS
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,  # Allows specific origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all HTTP methods
        allow_headers=["*"],  # Allows all headers
    )
