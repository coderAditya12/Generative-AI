"""
Configuration module for YouTube Transcript Downloader.
Centralizes all settings, API keys, and constants.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Keys
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")  # If you use a separate env var

# File Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE_PATH = os.path.join(SCRIPT_DIR, "data.json")

# Model Configuration
EMBEDDING_MODEL = "models/text-embedding-004"
LLM_MODEL = "gemini-2.5-flash"

# Pinecone Configuration
PINECONE_INDEX_NAME = "chatbot"

# Text Splitting Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Search Configuration
SEARCH_K = 10  # Number of similar documents to retrieve
