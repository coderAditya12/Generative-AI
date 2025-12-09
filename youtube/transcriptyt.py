from youtube_transcript_api import YouTubeTranscriptApi
import json
import os

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
print(script_dir)
data_file_path = os.path.join(script_dir, "data.json")
print(data_file_path)

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


def main():
    print("hello! welcome to youtube transcript downloader")
    youtube_id = input("enter the youtube url")
    if "=" in youtube_id:
        youtube_id = youtube_id.split("v=")
        youtube_id = youtube_id[1]
    call = ApiCall(youtube_id)
    #chucking the transcript
    
    print(call)


main()
