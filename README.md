# YouTube文字起こし取得アプリケーション

## 機能概要

- YouTube動画IDから文字起こしデータを取得
- URLからビデオIDを自動抽出
- 日本語・英語の文字起こしに対応
- エラー状況を適切に処理
- モダンなNext.jsベースのフロントエンドUI

## プロジェクト構造

```
youtube-content-processor2/
├── main.py                 # バックエンドアプリケーション
├── README.md              # 説明ドキュメント
├── .gitignore            # Gitの除外設定
└── frontend/             # フロントエンドアプリケーション
    ├── src/              # ソースコード
    │   └── app/         # Next.jsアプリケーション
    │       ├── favicon.ico
    │       ├── globals.css
    │       ├── layout.tsx
    │       └── page.tsx
    ├── public/          # 静的ファイル
    │   ├── file.svg
    │   ├── globe.svg
    │   ├── next.svg
    │   ├── vercel.svg
    │   └── window.svg
    ├── package.json     # npmパッケージ設定
    ├── package-lock.json # パッケージバージョンロック
    ├── tsconfig.json    # TypeScript設定
    ├── next.config.ts   # Next.js設定
    ├── postcss.config.mjs # PostCSS設定
    ├── eslint.config.mjs  # ESLint設定
    ├── .gitignore      # フロントエンド用Gitの除外設定
    └── README.md       # フロントエンド説明
```

## 環境要件

### バックエンド
- Python 3.11以上
- 依存パッケージ: fastapi, uvicorn, youtube-transcript-api

### フロントエンド
- Node.js 18以上
- npm 9以上
- TypeScript 5以上
- Next.js 14以上

## セットアップ

### バックエンド

```bash
# パッケージインストール
pip install fastapi uvicorn youtube-transcript-api

# 実行
python main.py
```

### フロントエンド

```bash
# フロントエンドディレクトリに移動
cd frontend

# パッケージインストール
npm install

# 開発サーバー起動
npm run dev
```

## 使用方法

1. バックエンドとフロントエンドの両方のサーバーを起動
2. ブラウザで http://localhost:3000 にアクセス
3. YouTubeのURLまたはビデオIDを入力
4. 「文字起こし取得」ボタンをクリック

## API仕様

### リクエスト

```json
{
  "video_id": "dQw4w9WgXcQ"
}
```
または
```json
{
  "video_id": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

### レスポンス

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

## 注意事項

- 文字起こしが無効な動画や指定言語の字幕がない場合はエラー
- バックエンドはローカル環境（http://127.0.0.1:8000）での実行を想定
- 本番環境デプロイには追加設定が必要