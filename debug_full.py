from youtube_transcript_api import YouTubeTranscriptApi
import sys

with open("debug_output.txt", "w") as f:
    f.write(f"Python: {sys.executable}\n")
    f.write(f"Attributes: {dir(YouTubeTranscriptApi)}\n")
    try:
        import youtube_transcript_api
        f.write(f"Version: {getattr(youtube_transcript_api, '__version__', 'Unknown')}\n")
    except:
        pass
