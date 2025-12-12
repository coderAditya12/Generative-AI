from youtube_transcript_api import YouTubeTranscriptApi
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from dotenv import load_dotenv
import json
import os

# Load environment variables from .env file
load_dotenv()

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
data_file_path = os.path.join(script_dir, "data.json")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
# Load data from JSON file, or initialize with empty list if file doesn't exist or is empty
# embedding model
embeddings = GoogleGenerativeAIEmbeddings(model="models/text-embedding-004")

pc = Pinecone(api_key=pinecone_api_key)
index = pc.Index(
    "chatbot",
)

vector_store = PineconeVectorStore(index=index, embedding=embeddings)
DOCUMENT = []
try:
    with open(data_file_path, "r") as f:
        data = json.load(f)

except (FileNotFoundError, json.JSONDecodeError):
    data = []

DATA = data
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

def upload_to_pinecone(chunks, youtube_id):
    documents = []
    for chunk in chunks:
        documents.append(
            Document(page_content=chunk, metadata={"source_video": youtube_id})
        )

    # print(documents)
    doc_ids = vector_store.add_documents(documents)
    print(f"✓ Uploaded {len(doc_ids)} chunks to Pinecone")
    return doc_ids


def save_data():
    with open(data_file_path, "w") as f:
        json.dump(DATA, f, indent=2)


def cleanData(snippets):
    transcript = ""
    for snippet in snippets:
        transcript += snippet.text
    return transcript


def check_url(youtube_id):
    for i in range(0, len(data)):
        if DATA[i]["videoId"] == youtube_id:
            return i
    return -1


def ApiCall(youtube_id):
    index = check_url(youtube_id)
    if index != -1:
        return DATA[index]["transcript"]
    yt_api = YouTubeTranscriptApi()
    response = yt_api.fetch(youtube_id)
    filteredData = cleanData(response.snippets)

    return filteredData


def splitText(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = text_splitter.split_text(text)

    return chunks


def llmCall(userQuery, results):
    messages = [
        (
            "system",
            "You are a helpful assistant that can answer questions about a given topic based on the provided context.",
        ),
        ("human", f"Context: {results}\n\nQuestion: {userQuery}"),
    ]

    response = llm.invoke(messages)
    print(response.content)


def main():
    print("hello! welcome to youtube transcript downloader")
    youtube_id = input("enter the youtube url")
    if "=" in youtube_id:
        youtube_id = youtube_id.split("=")
        youtube_id = youtube_id[1]
        if "&" in youtube_id:
            youtube_id = youtube_id.split("&")[0]
    chunkCall = ApiCall(youtube_id)
    # chucking the transcript
    print(len(chunkCall))
    if chunkCall:
        chunks = splitText(chunkCall)
        DATA.append({"videoId": youtube_id, "transcript": chunks})
        save_data()
        upload_chunks = upload_to_pinecone(chunks, youtube_id)

        if upload_chunks:
            userQuery = input("what you want to know")
            
            results = vector_store.similarity_search(
                
                userQuery,
                k=10,
                filter={"source_video": youtube_id},
            )
            llmCall(userQuery, results)
            print(results)


main()
