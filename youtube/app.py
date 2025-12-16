"""
Streamlit UI for YouTube Transcript Downloader
A modern web interface for processing YouTube videos and asking questions.
"""

import streamlit as st
from transcript import ApiCall, extract_video_id
from chunking import splitText
from data_manager import load_data, save_data, add_transcript
from pinecone_manager import initialize_pinecone, upload_to_pinecone, search_similar
from llm_handler import initialize_llm, query_llm
from config import SEARCH_K


# Page configuration
st.set_page_config(
    page_title="YouTube Transcript Q&A",
    page_icon="🎥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for better styling
st.markdown(
    """
    <style>
    /* Main app styling */
    .main {
        padding: 2rem;
        background-color: #f8f9fa;
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        font-size: 16px;
        border: 2px solid #dee2e6;
        border-radius: 8px;
    }
    
    /* Chat message containers */
    .chat-message {
        padding: 1.2rem;
        border-radius: 12px;
        margin-bottom: 1rem;
        border: 1px solid #dee2e6;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    /* User message styling - Blue theme */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-left: 4px solid #5a67d8;
    }
    
    .user-message strong {
        color: #fff;
        font-size: 0.9rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Assistant message styling - Gray/Green theme */
    .assistant-message {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        color: #2d3748;
        border-left: 4px solid #48bb78;
    }
    
    .assistant-message strong {
        color: #2d3748;
        font-size: 0.9rem;
    }
    
    /* Video info card */
    .video-info {
        padding: 1.5rem;
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        border-radius: 12px;
        margin-bottom: 1.5rem;
        border: 2px solid #f6ad55;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .video-info h4 {
        margin: 0;
        color: #744210;
        font-size: 1.2rem;
    }
    
    .video-info p {
        margin: 0.5rem 0 0 0;
        color: #975a16;
    }
    
    /* Info boxes */
    .stInfo {
        background-color: #e6f3ff !important;
        border-left: 4px solid #3b82f6 !important;
    }
    
    /* Success boxes */
    .stSuccess {
        background-color: #d1fae5 !important;
        border-left: 4px solid #10b981 !important;
    }
    
    /* Warning boxes */
    .stWarning {
        background-color: #fef3c7 !important;
        border-left: 4px solid #f59e0b !important;
    }
    
    /* Error boxes */
    .stError {
        background-color: #fee2e2 !important;
        border-left: 4px solid #ef4444 !important;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background-color: #1e293b;
    }
    
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        color: #f1f5f9;
    }
    
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] label {
        color: #cbd5e1;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
    
    /* Metric cards */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
        font-weight: 700;
        color: #60a5fa;
    }
    
    /* Dividers */
    hr {
        margin: 1.5rem 0;
        border: none;
        border-top: 2px solid #e5e7eb;
    }
    </style>
""",
    unsafe_allow_html=True,
)


def initialize_services():
    """Initialize vector store and LLM (cached in session state)."""
    if "vector_store" not in st.session_state:
        with st.spinner("🔧 Initializing services..."):
            st.session_state.vector_store = initialize_pinecone()
            st.session_state.llm = initialize_llm()
            st.session_state.data = load_data()


def process_video(youtube_url):
    """Process a YouTube video: fetch, chunk, and upload to Pinecone."""
    try:
        video_id = extract_video_id(youtube_url)

        with st.spinner(f"📺 Fetching transcript for video: {video_id}..."):
            transcript = ApiCall(video_id, st.session_state.data)

        if not transcript:
            st.error("❌ Failed to fetch transcript. Please check the URL.")
            return None

        st.success(f"✅ Transcript fetched: {len(transcript)} characters")

        # Split into chunks
        with st.spinner("✂️ Splitting into chunks..."):
            chunks = splitText(transcript)

        st.info(f"📄 Split into {len(chunks)} chunks")

        # Save to cache
        st.session_state.data = add_transcript(st.session_state.data, video_id, chunks)
        save_data(st.session_state.data)

        # Upload to Pinecone
        with st.spinner("☁️ Uploading to vector database..."):
            upload_to_pinecone(st.session_state.vector_store, chunks, video_id)

        st.success("✅ Video processed successfully!")

        return {
            "video_id": video_id,
            "transcript": transcript,
            "chunks": chunks,
            "chunk_count": len(chunks),
        }

    except Exception as e:
        st.error(f"❌ Error processing video: {str(e)}")
        return None


def answer_question(question, video_id):
    """Answer a question based on the video transcript."""
    try:
        with st.spinner("🔍 Searching for relevant information..."):
            results = search_similar(
                st.session_state.vector_store, question, video_id, k=SEARCH_K
            )

        with st.spinner("🤖 Generating answer..."):
            answer = query_llm(st.session_state.llm, question, results)

        return answer, results

    except Exception as e:
        st.error(f"❌ Error answering question: {str(e)}")
        return None, None


# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state.messages = []
if "current_video" not in st.session_state:
    st.session_state.current_video = None
if "video_info" not in st.session_state:
    st.session_state.video_info = None

# Initialize services
initialize_services()

# Sidebar
with st.sidebar:
    st.title("🎥 YouTube Transcript Q&A")
    st.markdown("---")

    # URL Input
    st.subheader("📺 Video Input")
    youtube_url = st.text_input(
        "Enter YouTube URL:",
        placeholder="https://www.youtube.com/watch?v=...",
        help="Paste a YouTube video URL to process",
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button("▶️ Process Video", use_container_width=True, type="primary"):
            if youtube_url:
                video_info = process_video(youtube_url)
                if video_info:
                    st.session_state.current_video = video_info["video_id"]
                    st.session_state.video_info = video_info
                    st.session_state.messages = []  # Clear chat history
            else:
                st.warning("⚠️ Please enter a YouTube URL")

    with col2:
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.rerun()

    st.markdown("---")

    # Current video info
    if st.session_state.video_info:
        st.subheader("📊 Current Video")
        st.info(f"**Video ID:** {st.session_state.current_video}")
        st.metric(
            "Transcript Length",
            f"{len(st.session_state.video_info['transcript'])} chars",
        )
        st.metric("Chunks", st.session_state.video_info["chunk_count"])

    st.markdown("---")

    # Instructions
    with st.expander("ℹ️ How to Use"):
        st.markdown("""
        1. **Enter YouTube URL** in the input above
        2. **Click "Process Video"** to fetch and analyze
        3. **Ask questions** about the video content
        4. **View answers** with AI-powered responses
        
        💡 **Tip**: The transcript is cached, so you won't need to reprocess the same video!
        """)

# Main content area
st.title("💬 Ask Questions About Your Video")

# Show instructions if no video is loaded
if not st.session_state.current_video:
    st.info(
        "👈 Start by entering a YouTube URL in the sidebar and clicking 'Process Video'"
    )
else:
    # Display video information
    with st.container():
        st.markdown(
            f"""
        <div class="video-info">
            <h4>📹 Current Video: {st.session_state.current_video}</h4>
            <p>Ask any questions about the video content below!</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    # Display chat history
    for message in st.session_state.messages:
        if message["role"] == "user":
            st.markdown(
                f"""
            <div class="chat-message user-message">
                <strong>You:</strong> {message["content"]}
            </div>
            """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                f"""
            <div class="chat-message assistant-message">
                <strong>🤖 Assistant:</strong><br>{message["content"]}
            </div>
            """,
                unsafe_allow_html=True,
            )

    # Question input
    st.markdown("---")
    question = st.text_input(
        "Your Question:",
        placeholder="What is this video about?",
        key="question_input",
        help="Ask anything about the video content",
    )

    col1, col2, col3 = st.columns([1, 1, 4])

    with col1:
        ask_button = st.button("🚀 Ask", use_container_width=True, type="primary")

    with col2:
        if st.button("🔄 New Question", use_container_width=True):
            st.rerun()

    # Handle question submission
    if ask_button and question:
        # Add user message to chat
        st.session_state.messages.append({"role": "user", "content": question})

        # Get answer
        answer, sources = answer_question(question, st.session_state.current_video)

        if answer:
            # Add assistant message to chat
            st.session_state.messages.append({"role": "assistant", "content": answer})

            # Show source count
            if sources:
                st.caption(
                    f"📚 Answer based on {len(sources)} relevant chunks from the transcript"
                )

            st.rerun()

    elif ask_button and not question:
        st.warning("⚠️ Please enter a question")

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "Built with ❤️ using Streamlit | Powered by Google Gemini & Pinecone"
    "</div>",
    unsafe_allow_html=True,
)
