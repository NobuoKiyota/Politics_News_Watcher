import os
import datetime
import re
import drive_manager
import config

def load_assets(user, keyword, use_drive=True):
    """
    Scans both local and Drive assets for the given user/keyword.
    Returns a list of dictionaries compatible with the article processor.
    """
    assets = []
    
    # 1. Local Scan (Keep existing logic)
    assets.extend(load_local_assets(user, keyword))
    
    # 2. Drive Scan
    if use_drive:
        try:
            print(f"  [Asset Loader] Scanning Drive for {user}/{keyword}...")
            drive_assets = load_drive_assets(user, keyword)
            print(f"  [Asset Loader] Found {len(drive_assets)} items on Drive.")
            assets.extend(drive_assets)
        except Exception as e:
            print(f"  [Asset Loader] Drive Scan Failed: {e}")
            
    return assets

def load_local_assets(user, keyword):
    local_items = []
    asset_dir = os.path.join("assets", user, keyword)
    if not os.path.exists(asset_dir):
        return []
        
    try:
        files = os.listdir(asset_dir)
        for f in files:
            if f.endswith(".txt"):
                path = os.path.join(asset_dir, f)
                parsed = parse_asset_content(path, is_file=True)
                if parsed:
                    local_items.append(parsed)
    except Exception as e:
        print(f"  [Asset Loader] Local Error: {e}")
    return local_items

def load_drive_assets(user, keyword):
    """
    Navigates Root -> User -> Keyword and lists all text/doc files.
    Recursively scans subfolders (e.g. YYYY-MM) to find everything.
    """
    drive_items = []
    
    # 1. Resolve Path: Root -> User -> Keyword
    root_id = config.DRIVE_ROOT_FOLDER_ID
    if not root_id: return []
    
    user_id = drive_manager.find_folder_by_name(user, root_id)
    if not user_id: return []
    
    keyword_id = drive_manager.find_folder_by_name(keyword, user_id)
    if not keyword_id: return []
    
    # 2. Recursive Scan from Keyword Folder
    # We want "everything" under this keyword folder.
    
    def recursive_scan(folder_id):
        items = []
        # List all contents (files and folders)
        service = drive_manager.get_drive_service()
        query = f"'{folder_id}' in parents and trashed=false"
        results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
        files = results.get('files', [])
        
        for f in files:
            fid = f['id']
            name = f['name']
            mime = f['mimeType']
            
            if mime == 'application/vnd.google-apps.folder':
                # Remove recursion depth limit effectively for now, assuming not too deep
                items.extend(recursive_scan(fid))
                
            elif mime == 'application/vnd.google-apps.document' or mime == 'text/plain':
                # Download content
                print(f"    -> Loading Drive File: {name}")
                content = drive_manager.download_file_content(fid, mime)
                if content:
                    parsed = parse_asset_content(content, filename=name, is_file=False)
                    if parsed:
                        items.append(parsed)
        return items

    return recursive_scan(keyword_id)

def parse_asset_content(source, filename="", is_file=False):
    """
    Parses content string or file path.
    Tries to detect structured format (Title/Link/etc).
    If not structured, treats as generic context info.
    """
    try:
        content = ""
        if is_file:
            # Source is path
            filename = os.path.basename(source)
            with open(source, "r", encoding="utf-8") as f:
                content = f.read()
        else:
            # Source is content string
            content = source
            
        lines = content.split("\n")
        item = {
            "title": filename, # Default
            "link": "",
            "content": "",
            "published": "",
            "source": "Drive Asset"
        }
        
        # Check Structured Format
        # (Same logic as before)
        header_end_idx = 0
        has_structure = False
        
        if len(lines) > 0 and lines[0].startswith("Title: "):
             has_structure = True
             
        if has_structure:
            for i, line in enumerate(lines):
                if line.startswith("Title: "):
                    item["title"] = line[7:].strip()
                elif line.startswith("Link: "):
                    item["link"] = line[6:].strip()
                elif line.startswith("Published: "):
                    item["published"] = line[11:].strip()
                elif line.strip() == "":
                    if i > 3: 
                       header_end_idx = i
                       break
            item["content"] = "\n".join(lines[header_end_idx+1:]).strip()
            
            if "_VIDEO_" in filename:
                 item["source"] = "YouTube Video (Audio Analysis)"
                 
        else:
            # Treat as raw document (Learning Material)
            item["content"] = content
            item["title"] = f"【資料】{filename}"
            
        return item
    except Exception as e:
        print(f"Error parsing asset {filename}: {e}")
        return None
