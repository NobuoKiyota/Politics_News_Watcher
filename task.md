# Politics News Watcher Task List

## Phase 1: データ基盤構築 (Data Infrastructure)
- [x] Google Cloud Platform (GCP) プロジェクト作成とAPI有効化 (Sheets, Drive, Gemini) <!-- id: 0 -->
- [x] サービスアカウントキー (JSON) の取得と `config/` への配置 <!-- id: 1 -->
- [x] Googleフォームの作成 (利用者, キーワード, 時間, Discord URL) <!-- id: 2 -->
- [x] 管理用スプレッドシートの作成とサービスアカウントへの共有 <!-- id: 3 -->
- [x] Python仮想環境の作成と依存ライブラリのインストール (`requirements.txt`) <!-- id: 4 -->

## Phase 2: 収集・保存ロジック (Collection & Storage)
- [x] `drive_manager.py`: Googleドライブへの保存機能の実装 (共有フォルダ対応済) <!-- id: 6 -->
- [x] `collector.py`: ニュース収集機能の実装 <!-- id: 5 -->
- [x] `vector_store.py`: ベクトル重複排除ロジックの実装 <!-- id: 7 -->

## Phase 3: AI推敲・配信 (AI Processing & Delivery)
- [x] `processor.py`: 仮清書・最終清書ロジックの実装 <!-- id: 8 -->
- [x] `discord_bot.py`: Webhook通知機能の実装 <!-- id: 9 -->
- [x] `scheduler.py`: 統合スケジュール管理の実装 <!-- id: 10 -->

## Phase 4: テスト・運用 (Testing & Deployment)
- [x] 結合テスト (全フローの動作確認) <!-- id: 11 -->
- [x] 運用マニュアル作成 (SYSTEM_MANUAL.md) <!-- id: 12 -->
- [x] クラウド運用ガイド作成 (GITHUB_ACTIONS_GUIDE.md) <!-- id: 13 -->

## Phase 5: プロジェクト完了 (Completion)
- [x] GitHubリポジトリへのプッシュ設定 <!-- id: 14 -->
- [x] Secrets登録と最終確認 <!-- id: 15 -->
