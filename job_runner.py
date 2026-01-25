import sys
import collector
import video_collector
import processor
import drive_manager
import vector_store
import datetime
import os

def run_job(keyword, user_name):
    """
    Executes the collection job for a specific keyword and user.
    """
    print(f"--- Starting Job: {keyword} ({user_name}) ---")
    
    # Initialize components
    store = vector_store.NewsVectorStore()
    
    # 1. Collect News
    data_list = collector.collect_news_for_keyword(keyword)
    print(f"Collected {len(data_list)} items.")
    
    new_count = 0
    skipped_count = 0
    
    for item in data_list:
        content = item['content']
        title = item['title']
        link = item['link']
        article_id = item['id']
        
        # 2. Check Vector Duplication
        # Threshold 0.2 means very similar. 0.3 is slightly looser.
        # "Unrelated" showed < 0.4 in tests, so let's stick to 0.15 for safety.
        is_dup = store.is_duplicate(content, threshold=0.15)
        
        if is_dup:
            print(f"  [Skip] Semantic Duplicate: {title[:20]}...")
            skipped_count += 1
            continue
            
        # 3. Save to Drive
        # Folder structure: [Root]/[User]/[Keyword]/[YYYY-MM]
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        folder_id = drive_manager.ensure_structure(user_name, keyword, date_str)
        
        # File name: YYYYMMDD_Title.txt
        safe_title = "".join([c for c in title if c.isalnum() or c in " -_"]).strip()[:50]
        filename = f"{date_str.replace('-','')}_{safe_title}.txt"
        
        # STATELESS DEDUPLICATION: Check if file exists in Drive
        if drive_manager.check_file_exists(folder_id, filename):
             print(f"  [Skip] Drive Duplicate: {filename}")
             skipped_count += 1
             continue
             
        file_content = f"Title: {title}\nLink: {link}\nPublished: {item['published']}\n\n{content}"
        
        try:
            drive_manager.upload_text_file(folder_id, filename, file_content)
            print(f"  [Saved to Drive] {filename}")
        except Exception as e:
            print(f"  [Drive Error] Failed to upload {filename}: {e}")
            # Fallback to local
            local_dir = os.path.join("assets", user_name, keyword)
            os.makedirs(local_dir, exist_ok=True)
            local_path = os.path.join(local_dir, filename)
            with open(local_path, "w", encoding="utf-8") as f:
                f.write(file_content)
            print(f"  [Saved Locally] {local_path}")

        # 4. Add to Vector Store (Do this regardless of save location if at least one succeeded)
        store.add_article(article_id, content, {"keyword": keyword, "user": user_name, "link": link})
        new_count += 1
            
    print(f"Job Complete. New: {new_count}, Skipped: {skipped_count}")

    # 5. Collect & Process Videos
    print(f"--- Starting Video Collection: {keyword} ---")
    video_list = video_collector.search_videos(keyword)
    print(f"Found {len(video_list)} videos.")
    
    v_new_count = 0
    v_skipped_count = 0
    
    for video in video_list:
        video_id = video['id']
        title = video['title']
        link = video['link']
        
        # Check duplicate (using Video ID as ID)
        if store.is_duplicate_id(video_id): # We need to ensure vector_store supports ID check or just use content check
             # content check is better if we want to avoid same content from different sources, but video ID is unique.
             # vector_store.is_duplicate checks content semantic.
             # Let's use check_file_exists for stateless dedupe first.
             pass
        
        # Stateless Dedupe
        folder_id = drive_manager.ensure_structure(user_name, keyword, datetime.datetime.now().strftime("%Y-%m-%d"))
        safe_title = "".join([c for c in title if c.isalnum() or c in " -_"]).strip()[:50]
        filename = f"{datetime.datetime.now().strftime('%Y-%m-%d').replace('-','')}_VIDEO_{safe_title}.txt"
        
        if drive_manager.check_file_exists(folder_id, filename):
             print(f"  [Skip] Drive Duplicate (Video): {filename}")
             v_skipped_count += 1
             continue

        # Fetch Transcript
        print(f"  Processing Video: {title}")
        raw_transcript = video_collector.get_transcript(video_id)
        
        if not raw_transcript:
            print("    No transcript found.")
            continue
            
        # Process with Gemini (Fix typos & Summarize)
        processed_data = processor.process_video_transcript(raw_transcript, title)
        cleaned_transcript = processed_data.get("cleaned_transcript", "")
        summary = processed_data.get("summary", "")
        
        if not cleaned_transcript:
            print("    Failed to process transcript.")
            continue
            
        # Save to Drive
        file_content = f"Title: {title}\nLink: {link}\nPublished: {video['published']}\nType: YouTube Video\n\n## AI Summary\n{summary}\n\n## Transcript (Corrected)\n{cleaned_transcript}"
        
        try:
            drive_manager.upload_text_file(folder_id, filename, file_content)
            print(f"  [Saved Video to Drive] {filename}")
        except Exception as e:
             # Fallback
            local_dir = os.path.join("assets", user_name, keyword)
            os.makedirs(local_dir, exist_ok=True)
            local_path = os.path.join(local_dir, filename)
            with open(local_path, "w", encoding="utf-8") as f:
                f.write(file_content)
            print(f"  [Saved Video Locally] {local_path}")
            
        # Add Summary to Vector Store (We use summary for semantic search/report generation context)
        # We store the SUMMARY and Transcript? Or just Summary?
        # If we want the final report to include this info, the summarizer needs to see it.
        # The summarizer pulls from `vector_store` usually? Or does `job_runner` return something?
        # `job_runner` doesn't return anything. `scheduler.py` calls `run_job`.
        # Wait, `scheduler.py` calls `run_job`, but `run_job` saves to Drive/VectorStore.
        # Then `scheduler.py` calls `processor.generate_intermediate_draft`?
        # Let's check `scheduler.py` logic.
        
        store.add_article(video_id, summary + "\n\n" + cleaned_transcript[:1000], {"keyword": keyword, "user": user_name, "link": link})
        v_new_count += 1
        
    print(f"Video Job Complete. New: {v_new_count}, Skipped: {v_skipped_count}")

if __name__ == "__main__":
    # CLI usage: python job_runner.py "Keyword" "UserName"
    if len(sys.argv) > 2:
        k = sys.argv[1]
        u = sys.argv[2]
        run_job(k, u)
    else:
        print("Usage: python job_runner.py <keyword> <user_name>")
