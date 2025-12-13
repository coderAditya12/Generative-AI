"""
Main orchestrator for YouTube Transcript Downloader.
Entry point for the application.
"""

import streamlit as st


from transcript import ApiCall
from chunking import splitText
from data_manager import load_data, save_data, add_transcript
from pinecone_manager import initialize_pinecone, upload_to_pinecone, search_similar
from llm_handler import initialize_llm, query_llm
from config import SEARCH_K


def extract_video_id(url_or_id):
    """
    Extract video ID from YouTube URL or return as-is if already an ID.

    Args:
        url_or_id: YouTube URL or video ID

    Returns:
        YouTube video ID
    """
    youtube_id = url_or_id
    if "=" in youtube_id:
        youtube_id = youtube_id.split("=")[1]
        if "&" in youtube_id:
            youtube_id = youtube_id.split("&")[0]
    return youtube_id


def main():
    """Main application flow."""
    print("Hello! Welcome to YouTube Transcript Downloader")

    # Initialize services
    print("Initializing services...")
    vector_store = initialize_pinecone()
    llm = initialize_llm()

    # Load cached data
    data = load_data()

    # Get YouTube URL from user
    youtube_url = input("Enter the YouTube URL: ")
    youtube_id = extract_video_id(youtube_url)

    # Fetch transcript (from cache or API)
    print(f"Fetching transcript for video: {youtube_id}")
    transcript = ApiCall(youtube_id, data)
    print(f"Transcript length: {len(transcript)} characters")

    if transcript:
        # Split into chunks
        chunks = splitText(transcript)
        print(f"Split into {len(chunks)} chunks")

        # Save to cache
        data = add_transcript(data, youtube_id, chunks)
        save_data(data)

        # Upload to Pinecone
        upload_to_pinecone(vector_store, chunks, youtube_id)

        # Query loop
        while True:
            user_query = input("\nWhat do you want to know? (or 'quit' to exit): ")

            if user_query.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            # Search for relevant chunks
            results = search_similar(vector_store, user_query, youtube_id, k=SEARCH_K)

            # Query LLM with context
            answer = query_llm(llm, user_query, results)
            print(f"\n{answer}\n")

            # Optionally show sources
            print(f"[Retrieved {len(results)} relevant chunks]")
    else:
        print("Failed to fetch transcript.")



if __name__ == "__main__":
    main()
