import gspread
import config

def inspect_sheets():
    try:
        gc = gspread.service_account(filename=config.SERVICE_ACCOUNT_FILE)
        sh = gc.open_by_key(config.SPREADSHEET_KEY)
        
        print("--- Worksheets ---")
        for ws in sh.worksheets():
            print(f"Sheet Name: '{ws.title}' (ID: {ws.id})")
            headers = ws.row_values(1)
            print(f"  Headers: {headers}")
            print("-" * 20)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect_sheets()
