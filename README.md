# YouTube文字起こし取得・要約アプリケーション

## 機能概要

- YouTube動画IDから文字起こしデータを取得
- URLからビデオIDを自動抽出
- GPT-4.1-nanoを使用した文字起こしの要約機能（OpenAI API使用）
- チャット機能を追加して、文字起こしや要約に基づいた質問を処理
- TypeScript + Next.jsのモダンなUI
- Cloud SQL（MySQL）を使用したデータベース保存機能
- Google Cloud Storage（GCS）を使用した要約データの保存機能
- Docker対応（バックエンド・フロントエンド両方）

## プロジェクト構造

```
youtube-content-processor2/
├── main.py                # FastAPIサーバー（API実装）
├── agents/
│   └── summarizer.py      # 要約処理（GPT-4.1-nano）
├── database/
│   ├── __init__.py        # データベースパッケージ初期化
│   ├── db_models.py       # データベースモデル定義
│   └── db_service.py      # データベース操作サービス
├── dev_tools/
│   ├── check_bucket_iam.py      # GCS権限チェックツール
│   └── credential_test.py       # 認証情報テストツール
├── frontend/          
│   ├── src/           
│   │   └── app/      
│   │       ├── globals.css
│   │       ├── layout.tsx
│   │       └── page.tsx
│   ├── public/             # 静的アセット
│   ├── Dockerfile          # フロントエンド用Docker設定
│   └── package.json        # フロントエンド依存関係
├── Dockerfile             # バックエンド用Docker設定
├── requirements.txt       # Python依存パッケージ
└── README.md
```

## セットアップ

### 環境変数の設定

`.env`ファイルを作成し、以下の環境変数を設定してください：

```
# OpenAI API設定
OPENAI_API_KEY=your_openai_api_key

# YouTube API設定
YouTube_API_KEY=your_youtube_api_key

# データベース設定
DB_USER=your_db_user
DB_PASS=your_db_password
DB_NAME=your_db_name
DB_HOST=your_db_host
DB_PORT=3306
INSTANCE_CONNECTION_NAME=your_cloud_sql_instance_connection_name

# Google Cloud Storage設定
GCS_BUCKET_NAME=your_gcs_bucket_name
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/credentials.json
```

### バックエンド

```bash
# 依存関係のインストール
pip install -r requirements.txt

# 実行
python main.py
```

### フロントエンド

```bash
cd frontend
npm install
npm run dev
```

### Cloud SQL接続

1. Cloud SQL Proxyのインストール
2. Cloud SQL Admin APIの有効化
   - GCPコンソールで有効化: https://console.developers.google.com/apis/api/sqladmin.googleapis.com/overview?project=youtube-content-processor2
3. ローカルMySQLサーバーが実行中の場合は停止（ポート3306が使用中の場合）
   - 実行中のプロセス確認: `netstat -ano | findstr :3306`
   - プロセスID確認: `tasklist | findstr <PID>`
   - サービス停止: `taskkill /F /PID <PID>` または services.mscから停止
4. Cloud SQL Proxyの実行
   ```bash
   cloud-sql-proxy youtube-content-processor2:asia-northeast1:youtube-content-processor2 --port=3306
   ```
   - 実行中はコマンドプロンプトを閉じないでください

### Google Cloud Storage（GCS）設定

1. GCSバケットの作成（存在しない場合）
2. サービスアカウントに適切な権限を付与:
   - Storage オブジェクト閲覧者 (roles/storage.objectViewer)
   - Storage オブジェクト作成者 (roles/storage.objectCreator)
3. 権限設定をテストするには:
   ```bash
   python dev_tools/check_bucket_iam.py
   python dev_tools/credential_test.py
   ```

### Dockerを使用した実行

バックエンド:
```bash
docker build -t youtube-content-processor-backend .
docker run -p 8000:8000 --env-file .env youtube-content-processor-backend
```

フロントエンド:
```bash
cd frontend
docker build -t youtube-content-processor-frontend .
docker run -p 3000:3000 youtube-content-processor-frontend
```

## 使い方

1. バックエンド(http://localhost:8000)とフロントエンド(http://localhost:3000)を起動
2. ブラウザでフロントエンドにアクセス
3. YouTubeのURLまたはビデオIDを入力フィールドに貼り付け
4. 「文字起こし取得」をクリックして字幕を取得
   - 日本語・英語の両方を自動で試行
5. 文字起こしが表示されたら「要約取得」をクリックして要約を生成
   - 要約データはデータベースとGCSに保存され、再度同じ動画の要約を要求した場合はキャッシュから読み込まれます
6. **チャットサイドバー**を利用して、文字起こしや要約に基づいた質問を行う
   - 入力フィールドに質問を入力し、送信ボタンをクリック
   - 「文字起こし」「要約」いずれかのモードで質問できます

## 技術スタック詳細

### バックエンド

- Python 3.12.9
- FastAPI: RESTful APIフレームワーク
- youtube-transcript-api: YouTube字幕取得ライブラリ
- langchain + OpenAI: GPT-4.1-nanoを使用した要約・チャット処理
- SQLAlchemy: データベースORM
- Google Cloud Storage: 要約データJSON保存
- MySQL（Cloud SQL）: 要約データの永続化

### フロントエンド

- Next.js 15.3.0: Reactフレームワーク
- React 19.0.0: UIライブラリ
- TypeScript: 型安全な開発
- TailwindCSS 4: ユーティリティファーストCSSフレームワーク
- ESLint 9: コード品質管理

## 要約機能の詳細

`agents/summarizer.py`では、GPT-4.1-nanoを使用して文字起こしテキストから構造化された要約を生成します。要約は以下の要素を含みます：

- **サブタイトル**: 動画の主題を表す簡潔なタイトル
- **概要**: 動画の内容に関する簡潔な要約
- **主要トピック**: 動画で扱われる3-5個の主要トピック
- **重要ポイント**: 3-5個の重要ポイントとその説明
- **キーワード**: 動画の内容を表す5-8個のキーワード
- **アクションアイテム**: 視聴者が実践できる2-3個のアクション

要約生成プロセスでは、Chain-of-Thoughtアプローチを採用し、分析ステップと要約ステップの2段階で処理を行い、より高品質な要約を実現しています。

## チャット機能の詳細

- **エンドポイント:** `/chat/`
- **機能**: 文字起こしまたは要約に基づいた質問応答
- **使用モデル**: GPT-4.1-nano
- **インターフェース**: サイドバーUIで文字起こし/要約のコンテキストを切り替え可能

## データ永続化

1. **Cloud SQL（MySQL）**
   - `VideoSummary`テーブルに構造化された要約データを保存
   - 再要求時に高速に取得するためのキャッシュとして機能

2. **Google Cloud Storage（GCS）**
   - 要約データをJSON形式で保存
   - タイムスタンプとUUIDを含むユニークなファイル名で管理

## API仕様

### ルートエンドポイント: GET /

#### レスポンス
```json
{
  "message": "YouTube 文字起こし API へようこそ"
}
```

### 文字起こし取得: POST /transcript/

#### リクエスト
```json
{
  "video_id": "dQw4w9WgXcQ"
}
```

#### レスポンス
```json
{
  "video_id": "dQw4w9WgXcQ",
  "transcript": [
    {
      "text": "字幕テキスト",
      "start": 0.0,
      "duration": 2.5
    }
  ],
  "title": "動画タイトル",
  "description": "動画の説明",
  "channelTitle": "チャンネル名",
  "channelId": "チャンネルID"
}
```

### 要約生成: POST /summarize/

#### リクエスト
```json
{
  "video_id": "dQw4w9WgXcQ"
}
```

#### レスポンス
```json
{
  "video_id": "dQw4w9WgXcQ",
  "summary": "要約テキスト（JSON形式）",
  "gcs_path": "gs://bucket-name/summaries/video_id_timestamp_uuid.json"
}
```

#### エラーレスポンス例
```json
{
  "detail": "指定された言語の文字起こしが利用できません"
}
```

### チャット: POST /chat/

#### リクエスト
```json
{
  "content": "チャットでの質問内容",
  "type": "transcript", // または "summary"
  "contentText": "文字起こしまたは要約のテキスト"
}
```

#### レスポンス
```json
{
  "response": "AIからの返答内容"
}
```

## 開発注意事項

- OpenAI APIキーの設定が必須（環境変数：OPENAI_API_KEY）
- 文字起こしの取得には対象動画が字幕を持っている必要あり
- プロダクション環境では適切なCORS設定が必要（現在はlocalhost:3000のみ許可）
- Cloud SQLとGCSの適切な権限設定が必要
- フロントエンドをカスタマイズする場合は、APIエンドポイントのURLを適宜変更

## トラブルシューティング

1. **Cloud SQL接続エラー**
   - Cloud SQL Proxyが正しく実行されているか確認
   - 環境変数が正しく設定されているか確認
   - ファイアウォール設定を確認

2. **GCS保存エラー**
   - サービスアカウントの権限を確認（`dev_tools/check_bucket_iam.py`を使用）
   - `GOOGLE_APPLICATION_CREDENTIALS`が正しく設定されているか確認

3. **文字起こし取得エラー**
   - 対象動画に字幕が存在するか確認
   - YouTube API Keyの有効性を確認

4. **要約生成エラー**
   - OpenAI APIキーの有効性と利用制限を確認
   - 大量のトークンを処理する場合は長い応答時間に注意

5. **フロントエンド接続エラー**
   - バックエンドのCORS設定を確認
   - APIエンドポイントURLが正しいか確認（デフォルトは`http://127.0.0.1:8000`）

## ライセンスと著作権

このアプリケーションはYouTubeコンテンツの個人的な視聴・学習を支援するために開発されています。動画コンテンツの著作権はYouTubeクリエイターに帰属します。文字起こしデータの取得と処理は、教育目的や個人利用の範囲内で行ってください。