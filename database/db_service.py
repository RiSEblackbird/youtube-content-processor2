import json
from sqlalchemy.exc import SQLAlchemyError
from .db_models import SessionLocal, VideoSummary
import traceback
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseService:
    """
    概要: データベース操作を行うサービスクラス
    用途: 要約データのDB保存と取得
    """
    
    @staticmethod
    def save_summary_to_db(video_id, summary_data, video_info, gcs_path=None):
        """
        概要: 要約データをデータベースに保存
        用途: 生成された要約データをCloud SQLに格納
        """
        # セッションの開始
        db = SessionLocal()
        try:
            # 要約データがJSON文字列の場合はパース
            if isinstance(summary_data, str):
                try:
                    summary_json = json.loads(summary_data)
                except json.JSONDecodeError:
                    logger.error(f"JSONデコードエラー: {summary_data[:100]}...")
                    return None
            else:
                summary_json = summary_data
            
            # データベースエントリの作成
            db_summary = VideoSummary(
                video_id=video_id,
                video_title=video_info.get("title", ""),
                video_description=video_info.get("description", ""),
                channel_title=video_info.get("channelTitle", ""),
                channel_id=video_info.get("channelId", ""),
                sub_title=summary_json.get("sub_title", ""),
                overview=summary_json.get("overview", ""),
                main_topics=summary_json.get("main_topics", []),
                keywords=summary_json.get("keywords", []),
                action_items=summary_json.get("action_items", []),
                key_points=summary_json.get("key_points", []),
                gcs_path=gcs_path
            )
            
            # データベースに追加とコミット
            db.add(db_summary)
            db.commit()
            db.refresh(db_summary)
            logger.info(f"データベースに要約を保存しました: video_id={video_id}, id={db_summary.id}")
            return db_summary.id
        except SQLAlchemyError as e:
            db.rollback()
            error_trace = traceback.format_exc()
            logger.error(f"データベース保存エラー: {str(e)}\n{error_trace}")
            return None
        except Exception as e:
            db.rollback()
            error_trace = traceback.format_exc()
            logger.error(f"予期せぬエラー: {str(e)}\n{error_trace}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_summary_by_video_id(video_id):
        """
        概要: ビデオIDから要約データを取得
        用途: 過去に保存した要約データの取得
        """
        db = SessionLocal()
        try:
            summary = db.query(VideoSummary).filter(VideoSummary.video_id == video_id).order_by(VideoSummary.created_at.desc()).first()
            if summary:
                # データベースのフィールドからJSONオブジェクトを再構築
                summary_data = {
                    "sub_title": summary.sub_title,
                    "overview": summary.overview,
                    "main_topics": summary.main_topics,
                    "keywords": summary.keywords,
                    "action_items": summary.action_items,
                    "key_points": summary.key_points
                }
                # summary_dataプロパティを追加
                summary.summary_data = summary_data
            return summary
        except Exception as e:
            logger.error(f"要約取得エラー: {str(e)}")
            return None
        finally:
            db.close()