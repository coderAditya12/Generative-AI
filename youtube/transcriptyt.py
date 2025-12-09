from youtube_transcript_api import YouTubeTranscriptApi
from langchain_text_splitters import RecursiveCharacterTextSplitter

import json
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
data_file_path = os.path.join(script_dir, "data.json")

# Load data from JSON file, or initialize with empty list if file doesn't exist or is empty
try:
    with open(data_file_path, "r") as f:
        data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    data = []

DATA = data


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
    DATA.append({"videoId": youtube_id, "transcript": filteredData})
    save_data()
    return filteredData


def splitText(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
    )
    chunks = text_splitter.split_text(text)
    return chunks


def main():
    print("hello! welcome to youtube transcript downloader")
    youtube_id = input("enter the youtube url")
    if "=" in youtube_id:
        youtube_id = youtube_id.split("v=")
        youtube_id = youtube_id[1]
    chunkCall = ApiCall(youtube_id)
    # chucking the transcript
    print(len(chunkCall))
    if chunkCall:
        chunks = splitText(chunkCall)
        print(chunks[0])
        print(chunks[1])


main()
