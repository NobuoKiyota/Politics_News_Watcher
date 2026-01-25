import drive_manager
import time

TARGET_EMAIL = "saku99atm5@gmail.com"

def cleanup_drive_quota():
    print("=== Drive Quota Cleanup Tool ===")
    print(f"Target Owner: {TARGET_EMAIL}")
    
    service = drive_manager.get_drive_service()
    
    # List files owned by me (Service Account)
    # q=" 'me' in owners and trashed=false "
    page_token = None
    total_moved = 0
    total_errors = 0
    
    while True:
        try:
            response = service.files().list(
                q="'me' in owners and trashed=false",
                fields="nextPageToken, files(id, name, mimeType, size)",
                pageToken=page_token
            ).execute()
        except Exception as e:
            print(f"Error listing files: {e}")
            break
            
        files = response.get('files', [])
        print(f"Found {len(files)} files in this batch...")
        
        for file in files:
            print(f"Processing: {file['name']} ({file.get('size', '0')} bytes)")
            
            # Skip folders? Usually folders don't take quota, but ownership matters for hierarchy.
            # Transfer everything.
            
            success = drive_manager.transfer_file_ownership(file['id'], TARGET_EMAIL)
            if success:
                total_moved += 1
            else:
                total_errors += 1
                
            # Throttling
            time.sleep(1.5)
            
        page_token = response.get('nextPageToken', None)
        if not page_token:
            break
            
    print(f"Cleanup Complete. Moved: {total_moved}, Errors: {total_errors}")

if __name__ == "__main__":
    cleanup_drive_quota()
