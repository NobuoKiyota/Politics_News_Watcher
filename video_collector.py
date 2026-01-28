import os
import datetime
import yt_dlp

def search_videos(keyword, max_results=5):
    """
    Search for recent videos related to the keyword using yt-dlp.
    Removes dependency on YouTube Data API.
    """
    print(f"Searching YouTube for: {keyword}...")
    
    # yt-dlp options for metadata search
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,  # robust and fast, gets metadata without downloading
        'noplaylist': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Search query: ytsearchN:keyword
            # Note: sorting by date in ytsearch is not directly strictly supported in string format 
            # as easily as API, but ytsearch usually gives relevant results.
            query = f"ytsearch{max_results}:{keyword}"
            result = ydl.extract_info(query, download=False)
            
            videos = []
            if 'entries' in result:
                for item in result['entries']:
                    title = item.get('title')
                    video_id = item.get('id')
                    
                    # yt-dlp sometimes returns slightly different structures depending on version
                    # But flat extraction usually gives these standard keys.
                    
                    upload_date = item.get('upload_date') # YYYYMMDD
                    
                    # Format date
                    published = upload_date
                    if upload_date and len(upload_date) == 8:
                        published = f"{upload_date[:4]}-{upload_date[4:6]}-{upload_date[6:]}"
                    
                    if not video_id:
                        continue

                    videos.append({
                        "id": video_id,
                        "title": title,
                        "link": f"https://www.youtube.com/watch?v={video_id}",
                        "published": published,
                        "channel": item.get('uploader')
                    })
            return videos
            
    except Exception as e:
        print(f"YouTube Search Error (yt-dlp): {e}")
        return []

def download_audio(video_id, output_dir="temp_audio"):
    """
    Downloads the audio of a video using yt-dlp.
    Returns the path to the downloaded file.
    """
    url = f"https://www.youtube.com/watch?v={video_id}"
    print(f"DEBUG: Downloading audio for {video_id}...")
    
    os.makedirs(output_dir, exist_ok=True)
    
    # yt-dlp options for best audio, compatible with Gemini (mp3/m4a/aac)
    # We'll target m4a (aac) or mp3 which are standard.
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_dir}/%(id)s.%(ext)s',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3', 
            'preferredquality': '192',
        }],
        'quiet': True,
        'no_warnings': True,
        # Improve resistance to "Sign in to confirm you’re not a bot"
        'extractor_args': {
            'youtube': {
                'player_client': ['android', 'web'],
                'player_skip': ['webpage', 'configs', 'js'],
                'innertube_client': ['android', 'web']
            }
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            
        # The file will be video_id.mp3
        file_path = os.path.join(output_dir, f"{video_id}.mp3")
        if os.path.exists(file_path):
            return file_path
        else:
             print(f"DEBUG: Download finished but file not found: {file_path}")
             return None
             
    except Exception as e:
        print(f"Error downloading audio for {video_id}: {e}")
        return None
