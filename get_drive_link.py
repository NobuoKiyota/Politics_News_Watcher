import drive_manager
from googleapiclient.discovery import build
import config

def get_link():
    try:
        service = drive_manager.get_drive_service()
        folder_name = "Politics_News_Watcher_Assets"
        
        # Search for folder
        query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
        results = service.files().list(q=query, fields="files(id, name, webViewLink, owners)").execute()
        files = results.get('files', [])
        
        if files:
            f = files[0]
            print(f"Found Folder: {f['name']}")
            print(f"ID: {f['id']}")
            print(f"Link: {f.get('webViewLink', 'No Link Found')}")
            print(f"Owner: {f['owners'][0]['emailAddress']}")
            
            # Try to share it with user? (We don't know user's email easily unless hardcoded or instructed)
            # But at least we can show the link.
        else:
            print("Folder not found.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_link()
