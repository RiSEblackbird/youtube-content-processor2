import sys
import traceback
import uvicorn
import json
import uuid
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import NoTranscriptAvailable, TranscriptsDisabled
from agents.summarizer import create_initial_summarizer, SummaryState
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.cloud import storage
from google.api_core import exceptions as google_exceptions
from database.db_models import create_tables
from database.db_service import DatabaseService

# .envファイルの読み込み
load_dotenv()

# 定数定義
API_TITLE = "YouTube 文字起こし API"
API_DESCRIPTION = "YouTube動画の文字起こしを取得するためのAPI"
API_VERSION = "1.0.0"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
YOUTUBE_URL_PREFIX = "https://www.youtube.com/watch?v="

# GCS設定
GCS_BUCKET_NAME = os.getenv('GCS_BUCKET_NAME')
GCS_SUMMARY_PREFIX = "summaries/"  # GCSのフォルダプレフィックス

def get_exception_trace() -> str:
    '''例外のトレースバックを取得'''
    return traceback.format_exc()


class TranscriptRequest(BaseModel):
    '''
    概要: 文字起こしリクエストのデータモデル \n
    用途: APIリクエストのボディを定義する
    '''
    video_id: str


class TranscriptResponse(BaseModel):
    '''
    概要: 文字起こしレスポンスのデータモデル \n
    用途: APIレスポンスの形式を定義する
    '''
    video_id: str
    transcript: List[Dict[str, Any]]
    title: str = ""
    description: str = ""
    channelTitle: str = ""
    channelId: str = ""


class SummaryResponse(BaseModel):
    video_id: str
    summary: str
    gcs_path: Optional[str] = None


class GoogleCloudStorageService:
    '''
    概要: Google Cloud Storageとの連携を行うサービス \n
    用途: データをGCSに保存する
    '''
    
    @staticmethod
    def initialize_client():
        '''GCSクライアントの初期化'''
        try:
            # 環境変数GOOGLE_APPLICATION_CREDENTIALSで認証情報が設定されていることを前提
            return storage.Client()
        except Exception as e:
            print(f"GCSクライアントの初期化に失敗しました: {str(e)}")
            return None

    @staticmethod
    def save_summary_to_gcs(video_id: str, summary_data: dict, video_info: dict) -> Optional[str]:
        '''
        概要: 要約データをGCSに保存する \n
        用途: 生成された要約データとビデオ情報をJSONとしてGCSに保存
        '''
        if not GCS_BUCKET_NAME:
            print("GCS_BUCKET_NAMEが設定されていません。GCSへの保存をスキップします。")
            return None
        
        try:
            client = GoogleCloudStorageService.initialize_client()
            if not client:
                return None
                
            bucket = client.bucket(GCS_BUCKET_NAME)
            
            # 現在時刻とUUIDでユニークなファイル名を生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = str(uuid.uuid4())[:8]
            filename = f"{GCS_SUMMARY_PREFIX}{video_id}_{timestamp}_{unique_id}.json"
            
            # 保存するデータの作成
            storage_data = {
                "video_id": video_id,
                "video_title": video_info.get("title", ""),
                "video_description": video_info.get("description", ""),
                "channel_title": video_info.get("channelTitle", ""),
                "channel_id": video_info.get("channelId", ""),
                "summary_data": summary_data,
                "timestamp": datetime.now().isoformat(),
            }
            
            # JSONデータの作成
            json_data = json.dumps(storage_data, ensure_ascii=False, indent=2)
            
            try:
                # GCSにアップロード
                blob = bucket.blob(filename)
                blob.upload_from_string(json_data, content_type="application/json")
                
                # 公開URLを返す（バケットが公開設定の場合）
                gcs_path = f"gs://{GCS_BUCKET_NAME}/{filename}"
                print(f"要約データを保存しました: {gcs_path}")
                return gcs_path
            
            except google_exceptions.Forbidden as e:
                error_message = "GCSへのアクセスが拒否されました。サービスアカウントに適切な権限が付与されていない可能性があります。"
                print(f"{error_message}\nエラー詳細: {str(e)}")
                return None
                
        except Exception as e:
            error_trace = traceback.format_exc()
            print(f"GCSへの保存中にエラーが発生しました: {str(e)}\n{error_trace}")
            return None


class YouTubeTranscriptService:
    '''
    概要: YouTube動画の文字起こしを取得するサービス \n
    用途: 指定されたYouTubeビデオIDの文字起こしを取得する
    '''

    @staticmethod
    def extract_video_id(url_or_id: str) -> str:
        '''
        概要: URLまたはビデオIDからビデオIDを抽出 \n
        用途: 完全なYouTube URLまたは短縮URLが提供された場合にビデオIDを取得する
        '''
        # youtu.be形式のURLに対応
        if "youtu.be" in url_or_id:
            return url_or_id.split("youtu.be/")[1].split("?")[0]
        # 通常のYouTube URL
        elif "youtube.com/watch" in url_or_id:
            return url_or_id.split("v=")[1].split("&")[0]
        # すでにビデオIDの場合
        return url_or_id

    @staticmethod
    def get_transcript(video_id: str) -> List[Dict[str, Any]]:
        '''
        概要: YouTube動画の文字起こしを取得 \n
        用途: 指定されたビデオIDの文字起こしをリストとして返す
        '''
        try:
            video_id = YouTubeTranscriptService.extract_video_id(video_id)
            transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=['ja', 'en'])
            return transcript
        except NoTranscriptAvailable:
            raise HTTPException(status_code=404, detail="指定された言語の文字起こしが利用できません")
        except TranscriptsDisabled:
            raise HTTPException(status_code=404, detail="この動画では文字起こしが無効になっています")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"文字起こしの取得中にエラーが発生しました: {str(e)}")

    @staticmethod
    def get_video_info(video_id: str) -> Dict[str, str]:
        '''
        概要: YouTube動画の情報を取得 \n
        用途: 指定されたビデオIDのタイトルと説明を取得する
        '''
        try:
            video_id = YouTubeTranscriptService.extract_video_id(video_id)
            
            if not os.getenv('YouTube_API_KEY'):
                print("YouTube APIキーが設定されていません")
                return {"title": "", "description": "", "channelTitle": "", "channelId": ""}

            youtube = build('youtube', 'v3', developerKey=os.getenv('YouTube_API_KEY'))
            request = youtube.videos().list(
                part='snippet',
                id=video_id
            )
            response = request.execute()

            if not response.get('items'):
                print(f"ビデオが見つかりません: {video_id}")
                return {"title": "", "description": "", "channelTitle": "", "channelId": ""}

            snippet = response['items'][0]['snippet']
            return {
                "title": snippet['title'],
                "description": snippet['description'],
                "channelTitle": snippet['channelTitle'],
                "channelId": snippet['channelId']
            }
        except HttpError as e:
            error_message = "YouTube APIエラー: "
            if e.status_code == 403:
                error_message += "APIキーの権限が不足しています。"
            else:
                error_message += f"{e.reason}"
            print(error_message)
            return {"title": "", "description": "", "channelTitle": "", "channelId": ""}
        except Exception as e:
            print(f"ビデオ情報の取得中にエラーが発生しました: {str(e)}")
            return {"title": "", "description": "", "channelTitle": "", "channelId": ""}


# FastAPIインスタンスの作成
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
)

# アプリケーション起動時にテーブルを作成
try:
    create_tables()
    print("データベーステーブルの作成に成功しました")
except Exception as e:
    print(f"警告: データベーステーブルの作成中にエラーが発生しました: {str(e)}")
    print(f"エラー詳細: {traceback.format_exc()}")
    print("アプリケーションは引き続き起動します...")
    # データベース接続エラーでもアプリケーションは起動する

# CORSミドルウェアの設定を追加
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # ローカル開発環境用
        "https://youtube-content-processor2-frontend-667890125929.asia-northeast1.run.app"  # 本番環境用
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    '''
    概要: ルートエンドポイント \n
    用途: APIが正常に動作していることを確認するための簡単なメッセージを返す
    '''
    return {"message": "YouTube 文字起こし API へようこそ"}


@app.post("/transcript/", response_model=TranscriptResponse)
async def get_video_transcript(request: TranscriptRequest):
    '''
    概要: 動画の文字起こしを取得するエンドポイント \n
    用途: 指定されたビデオIDの文字起こしを返す
    '''
    video_id = request.video_id
    transcript = YouTubeTranscriptService.get_transcript(video_id)
    video_info = YouTubeTranscriptService.get_video_info(video_id)
    return TranscriptResponse(
        video_id=video_id,
        transcript=transcript,
        title=video_info["title"],
        description=video_info["description"],
        channelTitle=video_info["channelTitle"],
        channelId=video_info["channelId"]
    )


@app.post("/summarize/", response_model=SummaryResponse)
async def get_video_summary(request: TranscriptRequest):
    """動画の文字起こしを要約するエンドポイント"""
    try:
        video_id = request.video_id
        transcript = YouTubeTranscriptService.get_transcript(video_id)
        video_info = YouTubeTranscriptService.get_video_info(video_id)
        
        # 既存の要約データをDBから検索（キャッシュとして使用）
        existing_summary = DatabaseService.get_summary_by_video_id(video_id)
        if existing_summary:
            print(f"既存の要約データを使用: video_id={video_id}")
            return SummaryResponse(
                video_id=video_id, 
                summary=json.dumps(existing_summary.summary_data),
                gcs_path=existing_summary.gcs_path
            )
        
        # 初期状態の作成
        initial_state = SummaryState(
            transcript=transcript,
            summary="",
            needs_refinement=True
        )
        
        # 要約ワークフローの作成と実行
        initial_summarizer = create_initial_summarizer()
        final_result = initial_summarizer.invoke(initial_state)
        
        try:
            # JSONとして解析可能か確認
            summary_json = json.loads(final_result['summary'])
            
            # GCSに保存
            gcs_path = GoogleCloudStorageService.save_summary_to_gcs(
                video_id=video_id,
                summary_data=summary_json,
                video_info=video_info
            )
            
            # データベースに保存
            db_id = DatabaseService.save_summary_to_db(
                video_id=video_id,
                summary_data=summary_json,
                video_info=video_info,
                gcs_path=gcs_path
            )
            
            if db_id:
                print(f"要約データをデータベースに保存しました: ID={db_id}")
            
            return SummaryResponse(
                video_id=video_id, 
                summary=final_result['summary'],
                gcs_path=gcs_path
            )
        except json.JSONDecodeError as je:
            raise HTTPException(
                status_code=500, 
                detail=f"要約のJSON解析に失敗しました。エラー位置: {je.pos}, 原因: {je.msg}\n生データ: {final_result['summary'][:200]}..."
            )
            
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"要約生成エラー: {str(e)}\nトレース:\n{error_trace}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=f"要約の生成中にエラーが発生しました: {str(e)}\n\n詳細:\n{error_trace}")


@app.post("/chat/", response_model=Dict[str, str])
async def process_chat(request: Dict[str, Any]):
    """チャットメッセージを処理するエンドポイント"""
    try:
        content = request.get("content", "")
        chat_type = request.get("type", "transcript")
        content_text = request.get("contentText", "")
        
        if not content or not content_text:
            raise ValueError("必要なパラメータが不足しています")

        llm = ChatOpenAI(model="gpt-4.1-nano", temperature=0)
        
        system_message = "文字起こし" if chat_type == "transcript" else "要約"
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"あなたは{system_message}の内容について質問に答える専門家です。"),
            ("user", f"以下の{system_message}の内容に関する質問に答えてください:\n\n{content_text}\n\n質問: {content}")
        ])
        
        formatted_prompt = prompt.format_messages()
        response = llm.invoke(formatted_prompt)
        return {"response": response.content}
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        error_trace = traceback.format_exc()
        print(f"チャット処理中にエラーが発生: {error_trace}", file=sys.stderr)
        raise HTTPException(status_code=500, detail=f"チャット処理中にエラーが発生しました: {str(e)}")


# メインプロセス
if __name__ == "__main__":
    try:
        # APIサーバーを起動
        uvicorn.run(app, host=DEFAULT_HOST, port=DEFAULT_PORT)
    except Exception as e:
        error_trace = get_exception_trace()
        print("エラーが発生しました:")
        for line in error_trace.splitlines():
            print(line)
        sys.exit(1)
