import sys
import collector
import video_collector
import processor
import drive_manager
import vector_store
import datetime
import os
import sheet_logger
import docs_manager

def run_job(keyword, user_name, doc_id=None, ignore_urls=None, context_text=""):
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
        
        # 1b. Strict Deduplication (Log Check)
        if ignore_urls and link in ignore_urls:
            print(f"  [Skip] Already in Spreadsheet Log: {title[:20]}...")
            skipped_count += 1
            continue
        
        # 2. Check Vector Duplication
        # Threshold 0.2 means very similar. 0.3 is slightly looser.
        # "Unrelated" showed < 0.4 in tests, so let's stick to 0.15 for safety.
        is_dup = store.is_duplicate(content, threshold=0.15)
        
        if is_dup:
            print(f"  [Skip] Semantic Duplicate: {title[:20]}...")
            skipped_count += 1
            continue
            
        # Ensure Drive Structure exists (Get Folder ID)
        if config.ENABLE_DRIVE_UPLOAD:
            folder_id = drive_manager.ensure_structure(user_name, keyword, date_str)
        else:
            folder_id = None
        
        # Local Directory
        local_dir = os.path.join("data", user_name, keyword)
        os.makedirs(local_dir, exist_ok=True)

        safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '-', '_')]).strip()
        filename = f"{datetime.datetime.now().strftime('%Y-%m-%d').replace('-','')}_{safe_title}.txt"
        
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
             
             # Upload to Drive
             if config.ENABLE_DRIVE_UPLOAD and folder_id:
                drive_manager.upload_text_file(folder_id, filename, file_content)
                print(f"  [Uploaded to Drive] {filename}")
             
        except Exception as e:
             print(f"  [Error] Failed to save locally/drive: {e}")
             
        except Exception as e:
             print(f"  [Error] Failed to save locally/drive: {e}")

        # Log to Sheet
        sheet_logger.log_item(user_name, keyword, "News", title, link)
        
        # Immediate Cloud Backup (Docs)
        if doc_id:
            docs_manager.append_text_to_doc(doc_id, f"【News】 {title}\nLink: {link}\n(Saved locally at {filename})\n")

        # 4. Add to Vector Store (Do this regardless of save location if at least one succeeded)
        store.add_article(article_id, content, {"keyword": keyword, "user": user_name, "link": link})
        
        # Update in-memory set to prevent duplicate in same batch
        if ignore_urls is not None:
            ignore_urls.add(link)
            
        new_count += 1
            
    print(f"Job Complete. New: {new_count}, Skipped: {skipped_count}")

    # 5. Collect & Process Videos
    if config.ENABLE_VIDEO_COLLECTION:
        print(f"--- Starting Video Collection: {keyword} ---")
        video_list = video_collector.search_videos(keyword, max_results=10)
        print(f"Found {len(video_list)} videos.")
        
        v_new_count = 0
        v_skipped_count = 0
        
        for video in video_list:
            video_id = video['id']
            title = video['title']
            link = video['link']
            
            # Strict Dedupe
            if ignore_urls and link in ignore_urls:
                 print(f"  [Skip] Video already logs: {title[:20]}...")
                 v_skipped_count += 1
                 continue
            
            # Check duplicate (using Video ID as ID)
            if store.is_duplicate_id(video_id): 
                 pass
            
            # Stateless Dedupe
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            
            # Ensure folder structure only if Drive Upload is enabled or we want to cache ID
            if config.ENABLE_DRIVE_UPLOAD:
                folder_id = drive_manager.ensure_structure(user_name, keyword, date_str)
            else:
                folder_id = None
            
            local_dir = os.path.join("assets", user_name, keyword)
            os.makedirs(local_dir, exist_ok=True)
            
            safe_title = "".join([c for c in title if c.isalnum() or c in (' ', '-', '_')]).strip()
            filename = f"{datetime.datetime.now().strftime('%Y-%m-%d').replace('-','')}_VIDEO_{safe_title}.txt"
            local_path = os.path.join(local_dir, filename)

            if os.path.exists(local_path):
                 print(f"  [Skip] Local Duplicate (Video): {filename}")
                 v_skipped_count += 1
                 continue
                 
            # Check Drive (Optional, but good for consistency)
            if config.ENABLE_DRIVE_UPLOAD and folder_id:
                if drive_manager.check_file_exists(folder_id, filename):
                     print(f"  [Skip] Drive Duplicate (Video): {filename}")
                     v_skipped_count += 1
                     continue

            # Perform Analysis
            print(f"  Processing Video: {title} ...")
            # Only download audio if enabled (redundant check but safe)
            audio_path = video_collector.download_audio(video_id)
            if not audio_path:
                print("  [Error] Audio Download Failed.")
                continue
                
            analysis = processor.process_video_audio(audio_path, title, context_text)
            
            # Clean up audio
            try: os.remove(audio_path)
            except: pass
            
            summary = analysis.get("summary", "No summary.")
            key_points = analysis.get("key_points", [])

            key_points_str = "\n".join([f"- {p}" for p in key_points])
            file_content = f"Title: {title}\nLink: {link}\nPublished: {video['published']}\nType: YouTube Video (Gemini Audio Analysis)\n\n## Gemini Audio Summary\n{summary}\n\n## Key Points\n{key_points_str}"
            
            try:
                 with open(local_path, "w", encoding="utf-8") as f:
                     f.write(file_content)
                 print(f"  [Saved Video Analysis Locally] {local_path}")
                 
                 # Upload to Drive
                 if config.ENABLE_DRIVE_UPLOAD and folder_id:
                     drive_manager.upload_text_file(folder_id, filename, file_content)
                     print(f"  [Uploaded Video to Drive] {filename}")
                 
            except Exception as e:
                 print(f"  [Error] Failed to save video locally/drive: {e}")
                
            store.add_article(video_id, summary + "\n\n" + key_points_str, {"keyword": keyword, "user": user_name, "link": link})
            
            # Log to Sheet
            sheet_logger.log_item(user_name, keyword, "Video", title, link)
            if ignore_urls is not None:
                ignore_urls.add(link)

            # Immediate Cloud Backup (Docs)
            if doc_id:
                video_report = f"【Video Analysis】 {title}\nLink: {link}\nPublished: {video['published']}\n\n[Summary]\n{summary}\n\n[Key Points]\n{key_points_str}\n"
                docs_manager.append_text_to_doc(doc_id, video_report)

            v_new_count += 1
            
        print(f"Video Job Complete. New: {v_new_count}, Skipped: {v_skipped_count}")
    else:
        print("Video Collection Disabled via Config.")

if __name__ == "__main__":
    # CLI usage: python job_runner.py "Keyword" "UserName"
    if len(sys.argv) > 2:
        k = sys.argv[1]
        u = sys.argv[2]
        run_job(k, u)
    else:
        print("Usage: python job_runner.py <keyword> <user_name>")
