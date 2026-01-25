import gspread
import datetime
import config

def get_log_worksheet():
    """
    Retrieves or creates the 'Processed_Log' worksheet.
    """
    try:
        gc = gspread.service_account(filename=config.SERVICE_ACCOUNT_FILE)
        sh = gc.open_by_key(config.SPREADSHEET_KEY)
        
        try:
            ws = sh.worksheet("Processed_Log")
        except gspread.exceptions.WorksheetNotFound:
            print("  [Logger] Creating 'Processed_Log' worksheet...")
            ws = sh.add_worksheet(title="Processed_Log", rows=1000, cols=10)
            # Add Header
            ws.append_row(["Date", "User", "Keyword", "Type", "Title", "URL"])
            
        return ws
    except Exception as e:
        print(f"  [Logger Error] Failed to access sheet: {e}")
        return None

def log_item(user, keyword, item_type, title, url):
    """
    Logs a processed item to the spreadsheet.
    """
    try:
        ws = get_log_worksheet()
        if not ws: return

        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Append row
        # gspread append_row is atomic enough for low volume
        ws.append_row([timestamp, user, keyword, item_type, title, url])
        print(f"  [Log] Added to Processed_Log: {title[:20]}...")
        
    except Exception as e:
        print(f"  [Logger Error] Failed to log item: {e}")
