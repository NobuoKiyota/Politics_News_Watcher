import schedule
import time
import datetime
import gspread
import config
import collector
import processor
import job_runner
import discord_bot
import docs_manager
import asset_loader
import sheet_logger

# Cache for jobs
sheet_cache = {
    "records": [],
    "worksheet_obj": None,
    "last_updated": None,
    "processed_urls": set()
}

def get_sheet_records():
    """
    Fetches records from Google Sheet.
    """
    try:
        gc = gspread.service_account(filename=config.SERVICE_ACCOUNT_FILE)
        sh = gc.open_by_key(config.SPREADSHEET_KEY)
        ws = sh.sheet1
        return ws.get_all_records(), ws
    except Exception as e:
        print(f"Sheet Error: {e}")
        return [], None

def update_config_cache():
    """
    Updates the global sheet cache.
    Scheduled to run hourly to save API calls.
    """
    print(f"\n[Scheduler] Updating Configuration Cache: {datetime.datetime.now().strftime('%H:%M:%S')}")
    records, ws = get_sheet_records()
    if ws:
        sheet_cache["records"] = records
        sheet_cache["worksheet_obj"] = ws
        sheet_cache["last_updated"] = datetime.datetime.now()
        
        # Update URL Cache for Deduplication
        p_urls = sheet_logger.get_processed_urls()
        sheet_cache["processed_urls"] = p_urls
        print(f"  -> Cache Updated. Loaded {len(records)} active jobs and {len(p_urls)} processed URLs.")
    else:
        print("  -> Failed to update cache. Keeping old config.")

def task_collection():
    print(f"\n[Scheduler] Running Hourly Collection Task: {datetime.datetime.now().strftime('%H:%M:%S')}")
    
    # Ensure cache is populated if empty
    if not sheet_cache["records"]:
        update_config_cache()
        
    records = sheet_cache["records"]
    
    # [CLOUD MODE ADAPTATION]
    # If using Cloud Mode (set via Env Var), we FORCE specific targets to avoid Sheet dependency issues on GHA.
    # Otherwise (Local), we rely on the Sheet.
    if config.IS_CLOUD_ENV:
        print("  [Cloud Mode] Using Hardcoded Priority Targets.")
        priority_targets = [
            {"利用者名": "System", "キーワード": "伊佐進一", "配信希望時間": "08:00", "Discord": config.DISCORD_WEBHOOK_URL},
            {"利用者名": "System", "キーワード": "岡本三成", "配信希望時間": "08:00", "Discord": config.DISCORD_WEBHOOK_URL},
            {"利用者名": "System", "キーワード": "斎藤鉄夫", "配信希望時間": "08:00", "Discord": config.DISCORD_WEBHOOK_URL},
            {"利用者名": "System", "キーワード": "中道改革連合", "配信希望時間": "08:00", "Discord": config.DISCORD_WEBHOOK_URL},
        ]
        # Force overwrite
        records = priority_targets
    
    # [Local Mode Handling]
    # If sheet is empty but we are Local, use a safeguard list.
    elif not records:
         print("  [Local Mode] Sheet appears empty. Using Safeguard Targets.")
         records = [
            {"利用者名": "System", "キーワード": "伊佐進一", "配信希望時間": "08:00", "Discord": config.DISCORD_WEBHOOK_URL},
         ]
    
    for row in records:
        user = row.get("利用者名") or row.get("利用者")
        keyword = row.get("キーワード") or row.get(" キ ー ワ ー ド")
        
        # Check if row is valid
        if not user or not keyword:
            continue
            
        print(f"  Processing: {user} / {keyword}")
        
        # Run collection
        # Handle multiple keywords separated by commas
        keyword_list = [k.strip() for k in keyword.split(",") if k.strip()]
        
        # Get Doc ID for Immediate Backup
        doc_id = row.get("Google Doc ID") or row.get("Doc ID")
        
        # Get Context Doc ID (Optional)
        ref_doc_id = row.get("Reference Doc ID") or row.get("Reference Docs") # Fallback to same Doc? No, unsafe.
        context_text = ""
        if ref_doc_id:
             print(f"    Loading Context from Doc: {ref_doc_id}")
             context_text = docs_manager.get_doc_content(ref_doc_id)
        
        existing_urls = sheet_cache.get("processed_urls", set())

        for k_item in keyword_list:
            try:
                job_runner.run_job(k_item, user, doc_id=doc_id, ignore_urls=existing_urls, context_text=context_text)
            except Exception as e:
                print(f"    Job Failed ({k_item}): {e}")
            time.sleep(2)

def task_delivery(force=False):
    now = datetime.datetime.now()
    current_time_str = now.strftime("%H:%M")
    today_str = now.strftime("%Y-%m-%d")
    
    # Use Cache instead of API call
    records = sheet_cache["records"]
    ws = sheet_cache["worksheet_obj"]
    
    # If cache is totally empty, try update once (e.g. first run)
    if not records:
        update_config_cache()
        records = sheet_cache["records"]
        ws = sheet_cache["worksheet_obj"]
    
    if not records or not ws: return

    for i, row in enumerate(records):
        # Row index in sheet: usually i + 2 (header is 1)
        # Note: If cache is old and rows changed, this might be risky. 
        # But assuming relatively static usage.
        row_idx = i + 2
        
        target_time = str(row.get("配信希望時間", "")).strip()
        # Handle formats like 8:00 vs 08:00
        if len(target_time) == 4 and target_time[1] == ":": target_time = "0" + target_time
        
        last_run = str(row.get("最終実行日 (System)", "")).strip()
        user = row.get("利用者名")
        keyword = row.get("キーワード")
        discord_url = row.get("通知先DiscordWebhook URL") or row.get("Discord")
        
        # Check timing
        # If force=True, ignore time check
        if force or (target_time == current_time_str and last_run != today_str):
            print(f"TRIGGER: Delivery for {user} ({keyword}) [Force: {force}]")
            
            try:
                # 1. Report Generation Logic
                # Use standard processor pipeline (fetching fresh data for report context)
                print("  Generating Report...")
                keyword_list = [k.strip() for k in keyword.split(",") if k.strip()]
                all_articles = []
                
                for k_item in keyword_list:
                    # 1a. Fetch Fresh Web News
                    k_articles = collector.collect_news_for_keyword(k_item)
                    all_articles.extend(k_articles)
                    time.sleep(1)
                    
                    # 1b. Load Local & Drive Assets (Context/Materials)
                    print(f"    Loading assets (Local + Drive) for {k_item}...")
                    # Changed from load_todays_assets to load_assets (includes Drive)
                    local_assets = asset_loader.load_assets(user, k_item, use_drive=True)
                    if local_assets:
                        print(f"    -> Found {len(local_assets)} assets.")
                        # Merge with deduplication based on Link
                        existing_links = {a['link'] for a in all_articles}
                        for asset in local_assets:
                            if asset['link'] not in existing_links:
                                all_articles.append(asset)
                                existing_links.add(asset['link'])
                
                processed = False
                if not all_articles:
                    print("    No articles (fresh or local) found.")
                    # Only send "No news" if strictly required, or maybe skip?
                    # User usually prefers silence over spam if nothing happening.
                    # But let's send "Nothing found" for confirmation.
                    try:
                        discord_bot.send_report(discord_url, f"【{keyword}】に関する本日の新しいニュースは見つかりませんでした。")
                        processed = True
                    except: pass
                else:
                    try:
                        draft = processor.generate_intermediate_draft(all_articles, keyword) 
                        final_report = processor.generate_final_report(draft)
                        print("  Sending to Discord...")
                        discord_bot.send_report(discord_url, final_report)
                        
                        # Google Docs Integration
                        doc_id = row.get("Google Doc ID") or row.get("Doc ID")
                        if doc_id:
                            print(f"  Appending to Google Doc: {doc_id}")
                            docs_success = docs_manager.append_daily_summary(doc_id, final_report)
                            if docs_success:
                                print("    -> Docs Append Success")
                            else:
                                print("    -> Docs Append Failed")
                                
                        processed = True
                    except Exception as e:
                        print(f"    Processing Error: {e}")
                
                # 3. Update Status (Write back to sheet)
                # We need to find the column index for "最終実行日 (System)" and "ステータス (System)"
                # Since we rely on cache, let's fetch header FRESH only when we write.
                # Just to be safe.
                if processed:
                    current_ws = get_sheet_records()[1] # Re-fetch WS to ensure connectivity
                    if current_ws:
                        headers = current_ws.row_values(1)
                        idx_last_run = -1
                        idx_status = -1
                        for ci, h in enumerate(headers):
                            if "最終実行日" in h: idx_last_run = ci + 1
                            if "ステータス" in h: idx_status = ci + 1
                        
                        if idx_last_run != -1:
                            current_ws.update_cell(row_idx, idx_last_run, today_str)
                        if idx_status != -1:
                            current_ws.update_cell(row_idx, idx_status, "Delivered")
                            
                    # Update cache in memory locally so we don't trigger again within same minute
                    row["最終実行日 (System)"] = today_str
                    
            except Exception as e:
                print(f"Delivery Error: {e}")

def main():
    print("--- Politics News Watcher Scheduler Started ---")
    print("Mode: Cached Config (Updates hourly)")
    
    # Update cache immediately on start
    update_config_cache()
    
    # Schedule Cache Update (Every 4 hours)
    schedule.every(4).hours.do(update_config_cache)
    
    # Schedule Collection every hour (at :05 to let config refresh first)
    schedule.every().hour.at(":05").do(task_collection)
    
    # Schedule Delivery Check every minute (uses cache)
    schedule.every().minutes.do(task_delivery)
    
    while True:
        schedule.run_pending()
        time.sleep(20)

if __name__ == "__main__":
    main()
