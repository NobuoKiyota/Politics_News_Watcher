import gspread
import config

def inspect():
    try:
        gc = gspread.service_account(filename=config.SERVICE_ACCOUNT_FILE)
        sh = gc.open_by_key(config.SPREADSHEET_KEY)
        ws = sh.sheet1
        headers = ws.row_values(1)
        print("--- Current Headers ---")
        for i, h in enumerate(headers):
            print(f"Col {i+1} ({chr(65+i)}): {h}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    inspect()
