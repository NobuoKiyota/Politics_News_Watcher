# 無料クラウド運用手順書 (GitHub Actions編)

PCをシャットダウンしても24時間システムを稼働させるため、**GitHub Actions** という無料機能を使ってクラウド上でプログラムを動かす手順です。
（正確には「常時起動」ではなく「スケジュールに従ってクラウドコンテナが立ち上がり、仕事をして終了する」バッチ処理です。このシステムに最適です。）

## 1. 準備するもの
- **GitHubアカウント** (無料)
- **リポジトリ**: このフォルダの中身（コード一式）をアップロードする場所

## 2. 設定ファイルの作成
`F:\Politics_News_Watcher\.github\workflows\schedule.yml` というファイルを新規作成し、以下の内容を記述します。
（これを作ると、GitHubが自動的にこのスケジュールを認識します）

```yaml
name: Politics News Watcher Scheduler

on:
  schedule:
    # 毎時0分に実行
    - cron: '0 * * * *'
  workflow_dispatch:

jobs:
  run-bot:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'

      - name: Install dependencies
        run: |
          pip install gspread google-api-python-client google-auth-httplib2 google-auth-oauthlib trafilatura newspaper3k discord-webhook python-dotenv schedule feedparser beautifulsoup4 requests chromadb google-generativeai youtube-transcript-api isodate

      - name: Run Scheduler Logic (Force Delivery Mode)
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
        run: |
          # Create service_account.json from Secret
          echo '${{ secrets.GCP_SA_JSON }}' > service_account.json
          
          # Run the cloud entry point
          python cloud_run.py
```

## 3. GitHubへの登録手順
1. GitHubで新しい「Private Repository（非公開リポジトリ）」を作成します。
2. 作成した `.github/workflows/schedule.yml` を含むコード一式をアップロードします。
3. リポジトリの **Settings > Secrets and variables > Actions** に移動します。
4. 以下の環境変数を登録します。
   - `GEMINI_API_KEY`: `.env` にあるAPIキー
   - `GCP_SA_JSON`: `service_account.json` の中身（テキスト）を丸ごとコピーして貼り付け

## 4. 運用イメージ
これだけで、GitHubのサーバーが **「毎時0分」に自動で立ち上がり**、`cloud_run.py` を実行して、Googleニュースを収集し、レポートをDiscordに送ってくれます。
あなたのPCは電源を切っていても構いません。

**注意点**:
- GitHub Actionsの無料枠は「月2000分」です。
- 1回の実行が1分であれば、2000回実行できます（1日24回 x 30日 = 720回 なので十分無料枠に収まります）。
