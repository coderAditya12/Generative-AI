"""
Pinecone manager module for vector store initialization and operations.
"""

from pinecone import Pinecone
from langchain_pinecone import PineconeVectorStore
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_core.documents import Document
from config import PINECONE_API_KEY, PINECONE_INDEX_NAME, EMBEDDING_MODEL


def initialize_pinecone():
    """Initialize Pinecone client and vector store."""
    # Initialize embeddings
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)

    # Initialize Pinecone
    pc = Pinecone(api_key=PINECONE_API_KEY)
    index = pc.Index(PINECONE_INDEX_NAME)

    # Create vector store
    vector_store = PineconeVectorStore(index=index, embedding=embeddings)

    return vector_store


def upload_to_pinecone(vector_store, chunks, youtube_id):
    """Upload document chunks to Pinecone."""
    documents = [
        Document(page_content=chunk, metadata={"source_video": youtube_id})
        for chunk in chunks
    ]

    doc_ids = vector_store.add_documents(documents)
    print(f"✓ Uploaded {len(doc_ids)} chunks to Pinecone")
    return doc_ids


def search_similar(vector_store, query, youtube_id, k=10):
    """Search for similar documents in Pinecone."""
    results = vector_store.similarity_search(
        query,
        k=k,
        filter={"source_video": youtube_id},
    )
    return results
