from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import config
import traceback

def check_apis():
    print("--- Checking Google Cloud APIs ---")
    
    # 1. Credentials
    print("1. Verifying Credentials File...")
    try:
        creds = config.get_service_account_credentials()
        print("   -> Credentials loaded successfully.")
        print(f"   -> Service Account Email: {creds.service_account_email}")
    except Exception as e:
        print("   -> FAILED to load credentials.")
        print(e)
        return

    # 2. Drive API
    print("\n2. Checking Google Drive API (List Files)...")
    try:
        service = build('drive', 'v3', credentials=creds)
        results = service.files().list(pageSize=5, fields="files(id, name)").execute()
        files = results.get('files', [])
        print("   -> Drive API Connection SUCCESS.")
        print(f"   -> Found {len(files)} files.")
        for f in files:
            print(f"      - {f['name']} ({f['id']})")
    except Exception as e:
        print("   -> Drive API FAILED.")
        print(f"   -> Error: {e}")

    # 3. Sheets API (access specific sheet)
    print(f"\n3. Checking Google Sheets API (Access Sheet: {config.SPREADSHEET_KEY})...")
    try:
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets().get(spreadsheetId=config.SPREADSHEET_KEY).execute()
        print("   -> Sheets API Connection SUCCESS.")
        print(f"   -> Sheet Title: {sheet.get('properties', {}).get('title')}")
    except Exception as e:
        print("   -> Sheets API FAILED.")
        print(f"   -> Error: {e}")
        # Check for specific error reasons
        if "HttpError 403" in str(e):
            if "Sheets API has not been used" in str(e):
                print("   !!! HINT: Google Sheets API might not be ENABLED in GCP Console.")
            elif "The caller does not have permission" in str(e):
                print("   !!! HINT: This is a PERMISSION error. Check sharing settings again.")

if __name__ == "__main__":
    check_apis()
