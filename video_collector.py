import os
import datetime
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import isodate

def get_youtube_service():
    """
    Returns an authenticated YouTube Data API service instance.
    Uses the same credentials logic, but requires YouTube Data API v3 enabled.
    """
    # Simply using the API Key for search if public data is enough, 
    # but since we have service account logic for Sheets/Drive, 
    # we might want to use API Key for YouTube Data API as it is simpler for search lists.
    # However, existing config uses service account. 
    # YouTube Data API supports API Key. Let's look for GEMINI_API_KEY? 
    # No, usually we need a specific API Key with YouTube enabled. 
    # Or we can use the Service Account if Domain-Wide Delegation is set, but that's complex.
    # EASIEST: Use the GEMINI_API_KEY if it is a general "Google Cloud API Key" that has YouTube enabled.
    # If not, user needs to enable it.
    
    api_key = os.getenv("GEMINI_API_KEY") # Asking user to ensure this key has YouTube Data API enabled.
    if not api_key:
        print("Error: GEMINI_API_KEY not found for YouTube API.")
        return None
        
    return build('youtube', 'v3', developerKey=api_key)

def search_videos(keyword, max_results=5):
    """
    Search for recent videos related to the keyword.
    """
    youtube = get_youtube_service()
    if not youtube:
        return []

    print(f"Searching YouTube for: {keyword}...")
    
    try:
        # Calculate time 24 hours ago (RFC 3339 formatted)
        published_after = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).isoformat() + "Z"
        
        request = youtube.search().list(
            part="snippet",
            q=keyword,
            type="video",
            order="date",
            publishedAfter=published_after,
            maxResults=max_results,
            relevanceLanguage="ja",
            regionCode="JP"
        )
        response = request.execute()
        
        videos = []
        for item in response.get("items", []):
            video_id = item["id"]["videoId"]
            title = item["snippet"]["title"]
            
            # Simple check to try and avoid Shorts (API doesn't strictly filter them in search easily without duration)
            # We will fetch details to check duration if strict filtering is needed, but for now let's just grab ID.
            
            videos.append({
                "id": video_id,
                "title": title,
                "link": f"https://www.youtube.com/watch?v={video_id}",
                "published": item["snippet"]["publishedAt"],
                "channel": item["snippet"]["channelTitle"]
            })
            
        return videos
        
    except Exception as e:
        print(f"YouTube Search Error: {e}")
        return []

def get_transcript(video_id):
    """
    Fetches the transcript for a video. 
    Prioritizes: Manual Japanese -> Auto Japanese.
    """
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        
        # Try to find a manually created Japanese transcript
        try:
            transcript = transcript_list.find_manually_created_transcript(['ja'])
        except NoTranscriptFound:
            # Fallback to auto-generated Japanese transcript
            try:
                transcript = transcript_list.find_generated_transcript(['ja'])
            except NoTranscriptFound:
                print(f"No Japanese transcript found for {video_id}")
                return None
        
        # Fetch the actual transcript data
        transcript_data = transcript.fetch()
        
        # Combine text
        full_text = " ".join([t['text'] for t in transcript_data])
        return full_text

    except (TranscriptsDisabled, NoTranscriptFound):
        print(f"Transcripts disabled or not found for {video_id}")
        return None
    except Exception as e:
        print(f"Error fetching transcript for {video_id}: {e}")
        return None
