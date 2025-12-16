"""
YouTube transcript fetching module.
"""

from youtube_transcript_api import YouTubeTranscriptApi


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


def cleanData(transcript_list):
    """
    Format: [00:12:30] The speaker said this text...
    """
    full_text = ""
    for snippet in transcript_list:
        # Convert seconds to HH:MM:SS format
        start_seconds = int(snippet.start)
        hours = start_seconds // 3600
        minutes = (start_seconds % 3600) // 60
        seconds = start_seconds % 60
        timestamp = f"[{hours:02}:{minutes:02}:{seconds:02}]"

        # Add timestamp to the text every few sentences
        # (Doing it for every line is too messy, so we do it simply here)
        full_text += f"{timestamp} {snippet.text} "

    return full_text


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
    response = yt_api.fetch(youtube_id, ["en", "hi"])
    filteredData = cleanData(response)

    return filteredData
