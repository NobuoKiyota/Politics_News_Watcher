from youtube_transcript_api import YouTubeTranscriptApi
import youtube_transcript_api
import sys

with open("debug_exp_output.txt", "w") as f:
    f.write(f"Module Dir: {dir(youtube_transcript_api)}\n")
    
    try:
        f.write("Trying YouTubeTranscriptApi.list('123')...\n")
        # Just check signature or if it crashes
        try:
            res = YouTubeTranscriptApi.list('123')
            f.write(f"list() returned: {type(res)}\n")
        except Exception as e:
            f.write(f"list() failed: {e}\n")
            
        f.write("Trying YouTubeTranscriptApi.fetch('123')...\n")
        try:
            res = YouTubeTranscriptApi.fetch('123')
            f.write(f"fetch() returned: {type(res)}\n")
        except Exception as e:
            f.write(f"fetch() failed: {e}\n")
            
    except Exception as e:
         f.write(f"Critical fail: {e}\n")
