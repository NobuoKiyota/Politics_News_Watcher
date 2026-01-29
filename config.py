import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project Base Path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Google Cloud Configuration
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, 'service_account.json')
SPREADSHEET_KEY = '1E4NHbpB_qD2EhLHhaMsyjAyrZ8DDIq_tuMZ6hl_2PYA' # Extracted from URL

# Gemini API Configuration (To be set in .env)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Feature Flags
# Set to False if running on Cloud/GitHub Actions to avoid blocking/quota issues
# Default to True for Local Laptop
IS_CLOUD_ENV = os.getenv("IS_CLOUD_ENV", "False").lower() == "true"

ENABLE_VIDEO_COLLECTION = not IS_CLOUD_ENV
ENABLE_DRIVE_UPLOAD = not IS_CLOUD_ENV

# Notification Configuration

# Notification Configuration
# Default Webhook URL (Used if not specified in Sheet)
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL", "https://discord.com/api/webhooks/1330882315579916328/F_7zP-8qHq9kHq... (Please set in Env or GitHub Secret for security)")

# Data Storage
DATA_DIR = os.path.join(BASE_DIR, 'data')
DRIVE_ROOT_FOLDER_ID = '1UtQ7h69qEurmG_Mt7MFov3YpKnTodB7G'  # Assets Root Folder

# Create necessary directories
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def get_service_account_credentials():
    from google.oauth2.service_account import Credentials
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(f"Service account file not found at {SERVICE_ACCOUNT_FILE}")
    
    creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=scopes)
    return creds
