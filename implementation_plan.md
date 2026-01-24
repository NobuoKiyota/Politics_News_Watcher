# Implementation Plan - Phase 1: Database Initialization

## Goal
Initialize the Google Spreadsheet to serve as the master database for the Politics News Watcher. This involves adding necessary administrative columns that are not part of the user-facing Google Form.

## User Review Required
> [!IMPORTANT]
> You need to add your Gemini API Key to the `.env` file after I create the template.

## Proposed Changes

### Configuration
#### [NEW] [.env](file:///F:/Politics_News_Watcher/.env)
- Create a `.env` file to store the `GEMINI_API_KEY`.

### Database Setup
#### [NEW] [setup_sheet.py](file:///F:/Politics_News_Watcher/setup_sheet.py)
- A script to:
    1. Connect to the Google Spreadsheet using `gspread` and `service_account.json`.
    2. Check if the "Form Responses 1" (or default) sheet exists.
    3. Ensure the header row contains the following columns:
        - Timestamp (A)
        - 利用者 (B)
        - キーワード (C)
        - 配信希望時間 (D)
        - Discord Webhook URL (E)
        - レポート設定 (F)
        - **[System] Google Drive ID** (G)
        - **[System] 最終実行日** (H)
        - **[System] ステータス** (I)
    4. If columns G, H, I are missing, append them to the header.

## Verification Plan
### Automated Verification
- Run `python setup_sheet.py`.
- The script will print the current headers and the result of the update.
- Check the Spreadsheet URL to visually confirm the new columns.
