import sys
import collector
import video_collector
import processor
import drive_manager
import vector_store
import datetime
import os
import sheet_logger

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
            
        # [Local Priority Mode]
        # Drive Upload Disabled due to Quota limits. Use Docs/Sheets for cloud access.
        # folder_id = drive_manager.ensure_structure(user_name, keyword, date_str)
        # if drive_manager.check_file_exists(folder_id, filename): ...

        local_dir = os.path.join("assets", user_name, keyword)
        os.makedirs(local_dir, exist_ok=True)
        local_path = os.path.join(local_dir, filename)
        
        # Simple File Existence Check
        if os.path.exists(local_path):
             print(f"  [Skip] Local Duplicate: {filename}")
             skipped_count += 1
             continue

        file_content = f"Title: {title}\nLink: {link}\nPublished: {item['published']}\n\n{content}"
        
        try:
             with open(local_path, "w", encoding="utf-8") as f:
                 f.write(file_content)
             print(f"  [Saved Locally] {local_path}")
        except Exception as e:
             print(f"  [Error] Failed to save locally: {e}")

        # Log to Sheet
        sheet_logger.log_item(user_name, keyword, "News", title, link)

        # 4. Add to Vector Store (Do this regardless of save location if at least one succeeded)
        store.add_article(article_id, content, {"keyword": keyword, "user": user_name, "link": link})
        new_count += 1
            
    print(f"Job Complete. New: {new_count}, Skipped: {skipped_count}")

    # 5. Collect & Process Videos
    print(f"--- Starting Video Collection: {keyword} ---")
    video_list = video_collector.search_videos(keyword, max_results=10)
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
        # [Local Priority Mode]
        # folder_id = drive_manager.ensure_structure(user_name, keyword, datetime.datetime.now().strftime("%Y-%m-%d"))
        local_dir = os.path.join("assets", user_name, keyword)
        os.makedirs(local_dir, exist_ok=True)
        filename = f"{datetime.datetime.now().strftime('%Y-%m-%d').replace('-','')}_VIDEO_{safe_title}.txt"
        local_path = os.path.join(local_dir, filename)

        if os.path.exists(local_path):
             print(f"  [Skip] Local Duplicate (Video): {filename}")
             v_skipped_count += 1
             continue

        # Save to Drive -> Disabled / Local Only
        key_points_str = "\n".join([f"- {p}" for p in key_points])
        file_content = f"Title: {title}\nLink: {link}\nPublished: {video['published']}\nType: YouTube Video (Gemini Audio Analysis)\n\n## Gemini Audio Summary\n{summary}\n\n## Key Points\n{key_points_str}"
        
        try:
             with open(local_path, "w", encoding="utf-8") as f:
                 f.write(file_content)
             print(f"  [Saved Video Analysis Locally] {local_path}")
        except Exception as e:
             print(f"  [Error] Failed to save video locally: {e}")
            
        store.add_article(video_id, summary + "\n\n" + key_points_str, {"keyword": keyword, "user": user_name, "link": link})
        
        # Log to Sheet
        sheet_logger.log_item(user_name, keyword, "Video", title, link)

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
