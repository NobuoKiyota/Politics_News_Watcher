# Politics News Watcher - Local Setup Guide

このプロジェクトを新しいPC（ローカル環境）にクローンして運用するための手順書です。

## 1. 必要な環境
- **Windows OS** (推奨)
- **Python 3.10 以上**
- **Git**
- **FFmpeg** (動画の音声抽出に必須)
- **Google Chrome** (Cookie抽出用)

## 2. セットアップ手順

### Step 1: クローン
```powershell
git clone https://github.com/NobuoKiyota/Politics_News_Watcher.git
cd Politics_News_Watcher
```

### Step 2: Python仮想環境の作成
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### Step 3: ライブラリのインストール
```powershell
pip install -r requirements.txt
```

### Step 4: 認証ファイルの配置
**重要**: セキュリティ上、Gitには含まれていない以下のファイルを、元のPCからコピーして配置してください。

1.  **`service_account.json`** (プロジェクトルート直下)
    *   Google Cloudの認証ファイルです。
2.  **`.env`** (プロジェクトルート直下)
    *   APIキーなどが記述された設定ファイルです。

### Step 5: FFmpegの確認
コマンドプロンプトで `ffmpeg -version` と打って反応があればOKです。
もしなければ、[公式サイト](https://ffmpeg.org/download.html)からダウンロードし、Pathを通してください。

## 3. 実行方法

### 通常モード（常時稼働）
バックグラウンドで動き続け、毎日決まった時間（08:00等）に配信します。
```powershell
python scheduler.py
```

### テスト実行（即時収集のみ）
特定のキーワードで収集・Drive保存だけテストしたい場合。
```powershell
python job_runner.py "伊佐進一" "System"
```

## 4. トラブルシューティング

### 動画の文字起こしが動かない
*   `yt-dlp` が最新か確認: `pip install -U yt-dlp`
*   Bot検知される場合: `config.py` の `ENABLE_VIDEO_COLLECTION` を確認

### Driveに保存されない
*   `config.py` の `ENABLE_DRIVE_UPLOAD` が `True` になっているか確認
*   `service_account.json` が正しいか確認
