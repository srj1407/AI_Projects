from youtube_transcript_api import YouTubeTranscriptApi
from urllib.parse import urlparse, parse_qs
import re

def get_video_id(url):
    # Handle youtu.be short links
    if "youtu.be" in url:
        return url.split("youtu.be/")[1].split("?")[0]
    
    # Handle full youtube.com URLs
    parsed = urlparse(url)
    video_id = parse_qs(parsed.query).get("v", [None])[0]
    return video_id

def get_transcripts(url):
    video_id = get_video_id(url)
    ytt_api = YouTubeTranscriptApi()
    fetched_transcript = ytt_api.fetch(video_id, languages = ['en', 'en-IN'])
    print(fetched_transcript)
    text = " ".join([t.text for t in fetched_transcript])
    return text[:1000]