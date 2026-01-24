import gspread
import config

def delete_duplicates():
    try:
        print("Connecting...")
        gc = gspread.service_account(filename=config.SERVICE_ACCOUNT_FILE)
        sh = gc.open_by_key(config.SPREADSHEET_KEY)
        ws = sh.sheet1
        
        # Current: 
        # F(6), G(7), H(8) are duplicates.
        # I(9), J(10), K(11) are correct system cols.
        # We need to delete 6, 7, 8.
        # Use simple delete_cols
        
        print("Deleting Columns F, G, H (indices 6, 7, 8)...")
        # delete_columns(start_index, end_index) 0-based or 1-based?
        # gspread uses 1-based usually.
        # But wait, documentation says delete_columns(index, end_index=None).
        # "Delete column at index. If end_index is specified, delete all columns from index to end_index."
        ws.delete_columns(6, 8) 
        
        print("Success! Columns I, J, K should now be F, G, H.")
        
        # Verify
        headers = ws.row_values(1)
        print("New Headers:", headers)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    delete_duplicates()
