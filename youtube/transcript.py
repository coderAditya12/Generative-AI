"""
YouTube transcript fetching module.
"""

from youtube_transcript_api import YouTubeTranscriptApi


def cleanData(snippets):
    """Convert transcript snippets to plain text."""
    transcript = ""
    for snippet in snippets:
        transcript += snippet.text
    return transcript


def check_url(youtube_id, data):
    """Check if transcript is already cached."""
    for i in range(len(data)):
        if data[i]["videoId"] == youtube_id:
            return i
    return -1


def ApiCall(youtube_id, data):
    """
    Fetch YouTube transcript, using cache if available.

    Args:
        youtube_id: YouTube video ID
        data: Cache of previously fetched transcripts

    Returns:
        Transcript text as string
    """
    # Check cache first
    index = check_url(youtube_id, data)
    if index != -1:
        # Return cached transcript (already chunked)
        # Joining chunks back to plain text
        cached = data[index]["transcript"]
        if isinstance(cached, list):
            return " ".join(cached)
        return cached

    # Fetch from YouTube API
    yt_api = YouTubeTranscriptApi()
    response = yt_api.fetch(youtube_id)
    filteredData = cleanData(response.snippets)

    return filteredData
