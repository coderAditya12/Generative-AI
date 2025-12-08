from youtube_transcript_api import YouTubeTranscriptApi
import json

# ask user for youtube id
youtube_id = "TXHF6_OS-tc"  # input("enter the youtube url")
# here is youtube link:-https://www.youtube.com/watch?v=-YeNbBi30oo
ytt_api = YouTubeTranscriptApi()
response = ytt_api.fetch(youtube_id)
# print(response.snippets)
transcript =""
for i in response.snippets:
    transcript += i.text
   
print(transcript)
