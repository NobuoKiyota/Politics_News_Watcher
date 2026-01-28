from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
import io
import config

ROOT_FOLDER_NAME = "Politics_News_Watcher_Assets"

def get_drive_service():
    creds = config.get_service_account_credentials()
    return build('drive', 'v3', credentials=creds)

def get_or_create_folder(folder_name, parent_id=None):
    service = get_drive_service()
    query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])

    if files:
        return files[0]['id']
    else:
        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if parent_id:
            file_metadata['parents'] = [parent_id]
        
        file = service.files().create(body=file_metadata, fields='id').execute()
        folder_id = file.get('id')
        
        # Grant permission to Main User
        try:
            service.permissions().create(
                fileId=folder_id,
                body={'role': 'writer', 'type': 'user', 'emailAddress': config.MAIN_USER_EMAIL},
                fields='id'
            ).execute()
        except: pass
        
        return folder_id

def upload_text_file(folder_id, filename, content):
    service = get_drive_service()
    
    # Check if file exists to overwrite or skip? 
    # For now, let's allow overwrite logic or versioning. 
    # Simple approach: Check existence, delete if exists (or update), then create.
    # But better to just create a new one for logs, or update for reports.
    # Let's clean up old ones if same name.
    
    query = f"name='{filename}' and '{folder_id}' in parents and trashed=false"
    results = service.files().list(q=query, fields="files(id)").execute()
    files = results.get('files', [])
    
    if files:
        # Update existing
        file_id = files[0]['id']
        file_metadata = {'name': filename} # Minimal update
        media = MediaIoBaseUpload(io.BytesIO(content.encode('utf-8')), mimetype='text/plain', resumable=True)
        updated_file = service.files().update(fileId=file_id, body=file_metadata, media_body=media).execute()
        return updated_file.get('id')
    else:
        # Create new
        file_metadata = {
            'name': filename,
            'parents': [folder_id],
            'mimeType': 'text/plain'
        }
        media = MediaIoBaseUpload(io.BytesIO(content.encode('utf-8')), mimetype='text/plain', resumable=True)
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        return file.get('id')

def check_file_exists(folder_id, filename):
    """
    Checks if a file exists in the given folder.
    Returns: file_id or None
    """
    if not folder_id: return None
    try:
        service = get_drive_service()
        query = f"name='{filename}' and '{folder_id}' in parents and trashed=false"
        results = service.files().list(q=query, fields="files(id)").execute()
        files = results.get('files', [])
        if files:
            return files[0]['id']
    except Exception as e:
        print(f"Drive Check Error: {e}")
    return None

def ensure_structure(user_name, keyword, date_str):
    """
    Creates/Ensures: Root -> YearMonth -> User_Keyword -> date
    Actually, plan said: [Root]/[YearMonth]/[Keyword]/
    Let's stick to: Root -> User -> Keyword -> YearMonth (or just straight to Keyword folder)
    
    Plan: [資産ルート]/[年月]/[議員・キーワード]/
    """
    if config.DRIVE_ROOT_FOLDER_ID:
        root_id = config.DRIVE_ROOT_FOLDER_ID
    else:
        root_id = get_or_create_folder(ROOT_FOLDER_NAME)
    
    # YearMonth (e.g., 2026-01)
    ym = date_str[:7] # YYYY-MM
    ym_id = get_or_create_folder(ym, parent_id=root_id)
    
    # Keyword Folder (Using User_Keyword to be safe or just Keyword?)
    # User might have same keyword. But maybe shared asset is better?
    # Let's use User_Keyword to avoid conflict if tone is different? 
    # Or just Keyword to share knowledge?
    # User requested: "個別でキーワードを分けて運用" -> So User/Keyword might be better.
    # Let's do: User -> Keyword -> files
    # But checking plan: [Root]/[YearMonth]/[Keyword]
    # Let's modify to: [Root]/[User]/[Keyword]/[YearMonth] to be very organized.
    
    user_id = get_or_create_folder(user_name, parent_id=root_id)
    keyword_id = get_or_create_folder(keyword, parent_id=user_id)
    ym_sub_id = get_or_create_folder(ym, parent_id=keyword_id)
    
    return ym_sub_id

def transfer_file_ownership(file_id, email_address):
    """
    Transfers ownership of a file to the specified email address.
    Note: detailed permissions might be needed.
    """
    service = get_drive_service()
    try:
        # 1. Grant Writer permission first (sometimes required before ownership transfer)
        # Actually for ownership transfer, we usually add permission with role='owner'.
        # But for consumer gmail, sometimes we can only do valid transfers if in same domain.
        # Let's try adding owner permission directly.
        
        permission_body = {
            'role': 'owner',
            'type': 'user',
            'emailAddress': email_address
        }
        # transferOwnership=True is required for changing owner.
        service.permissions().create(
            fileId=file_id,
            body=permission_body,
            transferOwnership=True,
            emailMessage="Automatically transferring file ownership to main account.",
            fields='id'
        ).execute()
        
        print(f"  [Drive] Transferred ownership of {file_id} to {email_address}")
        return True
    except Exception as e:
        print(f"  [Drive Transfer Error] Failed to transfer {file_id}: {e}")
        return False

def find_folder_by_name(folder_name, parent_id):
    """
    Finds a specific folder by name within a parent folder.
    Returns folder_id or None.
    """
    service = get_drive_service()
    if not parent_id:
        parent_id = config.DRIVE_ROOT_FOLDER_ID
    
    query = f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}' and trashed=false and '{parent_id}' in parents"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get('files', [])
    if files:
        return files[0]['id']
    return None

def list_files_in_folder(folder_id):
    """
    Lists all non-folder files in the given folder.
    Returns list of dicts: {'id', 'name', 'mimeType'}
    """
    service = get_drive_service()
    # Query for non-folder items
    query = f"'{folder_id}' in parents and mimeType != 'application/vnd.google-apps.folder' and trashed=false"
    results = service.files().list(q=query, fields="files(id, name, mimeType)").execute()
    return results.get('files', [])

def download_file_content(file_id, mime_type=None):
    """
    Downloads file content. 
    - Auto-exports Google Docs to text/plain.
    - Reads plain text directly.
    """
    service = get_drive_service()
    try:
        content = ""
        # Google Doc -> Export
        if mime_type == 'application/vnd.google-apps.document':
            request = service.files().export_media(fileId=file_id, mimeType='text/plain')
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            content = fh.getvalue().decode('utf-8')
            
        # Text/Other -> Get Media
        else:
            request = service.files().get_media(fileId=file_id)
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            # Try decode (utf-8)
            try:
                content = fh.getvalue().decode('utf-8')
            except:
                # Fallback implementation for binary or other encoding if needed
                pass
                
        return content
    except Exception as e:
        print(f"  [Drive Download Error] {file_id}: {e}")
        return ""
