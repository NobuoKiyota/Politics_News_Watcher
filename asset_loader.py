import os
import datetime
import re

def load_todays_assets(user, keyword, date_str=None):
    """
    Scans the local asset folder for the given user/keyword.
    Returns a list of dictionaries compatible with the article processor.
    """
    if not date_str:
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        
    date_compact = date_str.replace("-", "") # YYYYMMDD
    
    asset_dir = os.path.join("assets", user, keyword)
    if not os.path.exists(asset_dir):
        return []
        
    loaded_items = []
    
    try:
        files = os.listdir(asset_dir)
        for f in files:
            # Check if file starts with today's date (YYYYMMDD or YYYY-MM-DD logic)
            # job_runner uses: YYYYMMDD_Title.txt
            if f.startswith(date_compact) and f.endswith(".txt"):
                path = os.path.join(asset_dir, f)
                parsed = parse_asset_file(path)
                if parsed:
                    loaded_items.append(parsed)
                    
    except Exception as e:
        print(f"Asset Load Error: {e}")
        
    return loaded_items

def parse_asset_file(path):
    """
    Parses a saved text file back into a dictionary.
    Format:
    Title: ...
    Link: ...
    Published: ...
    [Type: ...]
    
    Body...
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        lines = content.split("\n")
        item = {
            "title": "",
            "link": "",
            "content": "",
            "published": "",
            "source": "Local Asset"
        }
        
        header_end_idx = 0
        for i, line in enumerate(lines):
            if line.startswith("Title: "):
                item["title"] = line[7:].strip()
            elif line.startswith("Link: "):
                item["link"] = line[6:].strip()
            elif line.startswith("Published: "):
                item["published"] = line[11:].strip()
            elif line.strip() == "":
                # Check if next line is main content? 
                # Usually we have double newline after headers.
                # Let's assume headers are top few lines.
                if i > 3: # Arbitrary header length check
                   header_end_idx = i
                   break
                   
        item["content"] = "\n".join(lines[header_end_idx+1:]).strip()
        
        # Identify if Video
        if "_VIDEO_" in os.path.basename(path):
             item["source"] = "YouTube Video (Audio Analysis)"
             
        return item
    except Exception as e:
        print(f"Error parsing {path}: {e}")
        return None
