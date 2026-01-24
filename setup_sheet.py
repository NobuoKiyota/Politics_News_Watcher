import gspread
import config

def setup():
    try:
        # Connect to Google Sheets
        gc = gspread.service_account(filename=config.SERVICE_ACCOUNT_FILE)
        sh = gc.open_by_key(config.SPREADSHEET_KEY)
        
        # Get the first sheet (usually form responses)
        worksheet = sh.sheet1
        
        # Get current headers
        headers = worksheet.row_values(1)
        print(f"Current headers: {headers}")
        
        # Define required headers
        # Assuming Form creates: Timestamp, 利用者, キーワード, 配信希望時間, Discord URL, レポート設定
        # We need to add system columns if they don't exist
        
        system_columns = [
            "Google Drive ID (System)",
            "最終実行日 (System)",
            "ステータス (System)"
        ]
        
        new_headers = []
        for col in system_columns:
            if col not in headers:
                new_headers.append(col)
        
        if new_headers:
            print(f"Adding new columns: {new_headers}")
            # Add new headers to the first row, after existing columns
            start_col = len(headers) + 1
            # gspread's update method: update(range_name, values=[[]])
            # Construct range, e.g., "G1:I1"
            # But simpler to just use update_cell or finding the right method.
            # update_cell is slow for multiple.
            # worksheet.update(values=[new_headers], range_name=...)
            
            # Let's just use a simple robust way: get all values, update row 1 locally, update whole row 1?
            # Or just append to row 1?
            # worksheet.resize(rows=1000, cols=len(headers) + len(new_headers)) # Ensure enough cols
            # Actually, just updating the specific cells is processed fine.
            
            # 1-based index
            for i, header in enumerate(new_headers):
                col_index = start_col + i
                worksheet.update_cell(1, col_index, header)
            
            print("Columns added successfully.")
        else:
            print("All system columns already exist.")
            
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error: {e}")

if __name__ == "__main__":
    setup()
