import drive_manager
from googleapiclient.discovery import build
import config
import os

def list_hidden_files():
    print("Searching for 'Politics_News_Watcher_Assets' in Service Account Drive...")
    try:
        service = drive_manager.get_drive_service()
        
        # Search by name, ignoring the config.DRIVE_ROOT_FOLDER_ID for a moment
        # We want to find the one created by SA (which might be the same name)
        query = "mimeType='application/vnd.google-apps.folder' and name='Politics_News_Watcher_Assets' and trashed=false"
        results = service.files().list(q=query, fields="files(id, name, createdTime)").execute()
        folders = results.get('files', [])
        
        if not folders:
            print("No hidden folder found.")
            return

        for folder in folders:
            f_id = folder['id']
            print(f"\nFound Folder: {folder['name']} (ID: {f_id})")
            
            # List contents recursively? Just top level or 2nd level.
            # Structure: Root -> User -> Keyword -> YYYY-MM -> File
            # Or Root -> YYYY-MM -> ...
            # Let's just list ALL text files inside this folder (recursive)
            # Use query with 'parents' is tricky for recursive.
            # Let's just look for headers.
            
            q_files = f"'{f_id}' in parents and trashed=false"
            res_files = service.files().list(q=q_files, fields="files(id, name, mimeType)").execute()
            children = res_files.get('files', [])
            
            print(f"  Contains {len(children)} items (Users/Folders).")
            for child in children:
                print(f"  - {child['name']} ({child['mimeType']})")
                
                # Dig deeper 1 level
                if child['mimeType'] == 'application/vnd.google-apps.folder':
                     q_sub = f"'{child['id']}' in parents and trashed=false"
                     res_sub = service.files().list(q=q_sub, fields="files(id, name, mimeType)").execute()
                     subs = res_sub.get('files', [])
                     for s in subs:
                         print(f"    - {s['name']}")
                         # Dig for files
                         if s['mimeType'] == 'application/vnd.google-apps.folder':
                             q_leaf = f"'{s['id']}' in parents and trashed=false"
                             res_leaf = service.files().list(q=q_leaf, fields="files(id, name)").execute()
                             leafs = res_leaf.get('files', [])
                             for l in leafs:
                                 print(f"      - {l['name']} (ID: {l['id']})")
                                 
                                 # Try Download
                                 try:
                                     content = service.files().get_media(fileId=l['id']).execute()
                                     safe_name = l['name'].replace("/","_")
                                     local_path = os.path.join("downloaded_assets", child['name'], s['name'])
                                     os.makedirs(local_path, exist_ok=True)
                                     with open(os.path.join(local_path, safe_name), "wb") as f:
                                         f.write(content)
                                     print(f"        [Downloaded] to {local_path}")
                                 except Exception as e:
                                     print(f"        [Download Failed] {e}")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import os
    if not os.path.exists("downloaded_assets"):
        os.makedirs("downloaded_assets")
    list_hidden_files()
