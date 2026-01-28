from video_collector import download_audio
import os

# Video ID that failed previously
video_id = "_Q3XGrYkGoQ" 
print(f"Testing download for {video_id}...")

path = download_audio(video_id, output_dir="test_dl_output")

if path and os.path.exists(path):
    print(f"SUCCESS: Downloaded to {path}")
else:
    print("FAILURE: Could not download audio.")
