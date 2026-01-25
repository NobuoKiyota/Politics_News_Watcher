from youtube_transcript_api import YouTubeTranscriptApi
import youtube_transcript_api
import sys

print("Python Executable:", sys.executable)
print("Library File:", youtube_transcript_api.__file__)
print("YouTubeTranscriptApi attributes:", dir(YouTubeTranscriptApi))

try:
    print("Calling get_transcript...")
    YouTubeTranscriptApi.get_transcript("123")
except Exception as e:
    print("Error:", e)
