#delete
from transcript import ApiCall
from chunking import splitText
from pinecone_upload import upload_to_pinecone
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_pinecone import PineconeVectorStore
from pinecone import Pinecone
from dotenv import load_dotenv
import json
import os

load_dotenv()

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
data_file_path = os.path.join(script_dir, "data.json")
pinecone_api_key = os.getenv("PINECONE_API_KEY")
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

jsonData = data
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")


def save_data():
    with open(data_file_path, "w") as f:
        json.dump(jsonData, f, indent=2)



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
        jsonData.append({"videoId": youtube_id, "transcript": chunks})
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
