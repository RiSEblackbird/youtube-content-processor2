# YouTube文字起こし取得API

## 機能概要

- YouTube動画IDから文字起こしデータを取得
- URLからビデオIDを自動抽出
- 日本語・英語の文字起こしに対応
- エラー状況を適切に処理

## プロジェクト構造

```
youtube-transcript-api/
├── main.py                 # メインアプリケーション
├── requirements.txt        # 依存パッケージリスト(一旦作成スキップ)
└── README.md               # 説明ドキュメント
```

## 環境要件

- Windows 10
- Python 3.11以上
- 依存パッケージ: fastapi, uvicorn, youtube-transcript-api

## セットアップ

```bash
# パッケージインストール
pip install fastapi uvicorn youtube-transcript-api

# 実行
python main.py

# 動作確認
# ブラウザで http://127.0.0.1:8000/docs にアクセス
```

## API使用例

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
    },
    // ...
  ]
}
```

## 注意事項

- 文字起こしが無効な動画や指定言語の字幕がない場合はエラー
- ローカル環境での実行を想定
- 本番環境デプロイには追加設定が必要