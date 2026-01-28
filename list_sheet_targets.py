import gspread
import config

def list_targets():
    try:
        gc = gspread.service_account(filename=config.SERVICE_ACCOUNT_FILE)
        sh = gc.open_by_key(config.SPREADSHEET_KEY)
        ws = sh.sheet1
        all_values = ws.get_all_values()
        headers = all_values[0]
        
        idx_user = -1
        idx_kw = -1
        
        for i, h in enumerate(headers):
            h = h.strip()
            if "利用者" in h: idx_user = i
            if "キーワード" in h: idx_kw = i
            
        print(f"User Col: {idx_user}, Keyword Col: {idx_kw}")
        
        for i, row in enumerate(all_values[1:]):
            if i > 5: break # Limit output
            if len(row) > idx_kw:
                print(f"Row {i+1}: User='{row[idx_user]}', Keywords='{row[idx_kw]}'")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    list_targets()
