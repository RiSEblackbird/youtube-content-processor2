# YouTube文字起こし取得・要約アプリケーション

## 機能概要

- YouTube動画IDから文字起こしデータを取得
- URLからビデオIDを自動抽出
- GPT-4を使用した文字起こしの要約機能（OpenAI API使用）
- チャット機能を追加して、文字起こしや要約に基づいた質問を処理
- TypeScript + Next.jsのモダンなUI

## プロジェクト構造

```
youtube-content-processor2/
├── main.py               # FastAPIサーバー（API実装）
├── agents/
│   └── summarizer.py    # 要約処理（GPT-4）
├── frontend/          
│   └── src/           
│       └── app/      
│           ├── globals.css
│           ├── layout.tsx
│           └── page.tsx
└── README.md
```

## セットアップ

### バックエンド

```bash
# 実行
python main.py
```

### フロントエンド

```bash
cd frontend
npm install
npm run dev
```

## 使い方

1. バックエンド(http://localhost:8000)とフロントエンド(http://localhost:3000)を起動
2. ブラウザでフロントエンドにアクセス
3. YouTubeのURLまたはビデオIDを入力フィールドに貼り付け
4. 「文字起こし取得」をクリックして字幕を取得
   - 日本語・英語の両方を自動で試行
5. 文字起こしが表示されたら「要約取得」をクリックして要約を生成
6. **新機能: チャットサイドバー**を利用して、文字起こしや要約に基づいた質問を行う
   - 入力フィールドに質問を入力し、送信ボタンをクリック

## 新機能: チャット機能

- **エンドポイント:** `/chat/`
- **使用例:**
  - 質問内容を送信すると、文字起こしまたは要約に基づいて回答が返されます。
  - フロントエンドのチャットUIには、ユーザーとAIのメッセージが表示されます。

## 環境要件

### バックエンド

- Python 3.12以上
- 依存パッケージ:
  - fastapi
  - uvicorn
  - youtube-transcript-api
  - langchain-openai
  - pydantic
  - python-dotenv

### フロントエンド

- Node.js 20以上
- 主要パッケージ:
  - Next.js 14
  - React 18
  - TailwindCSS

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
  ]
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
  "summary": "要約テキスト"
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