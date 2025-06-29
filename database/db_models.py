from sqlalchemy import Column, String, Text, DateTime, Integer, create_engine, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from datetime import datetime
from dotenv import load_dotenv

# .envファイルからの環境変数読み込み
load_dotenv()

# データベース接続情報
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "3306")  # MySQLのデフォルトポート
INSTANCE_CONNECTION_NAME = os.getenv("INSTANCE_CONNECTION_NAME")

# App EngineではなくCloud Run環境の検出方法を修正
if os.getenv("K_SERVICE") or os.getenv("GAE_ENV", "").startswith("standard"):
    # Cloud RunまたはApp Engineの場合、Unix socketを使用
    db_socket_dir = os.getenv("DB_SOCKET_DIR", "/cloudsql")
    cloud_sql_connection_name = INSTANCE_CONNECTION_NAME
    
    # ソケットパスの確認ログを追加
    socket_path = f"{db_socket_dir}/{cloud_sql_connection_name}"
    print(f"Cloud SQLソケットパス: {socket_path}")
    
    db_url = f"mysql+pymysql://{DB_USER}:{DB_PASS}@/{DB_NAME}?unix_socket={socket_path}"
    
    # 接続情報をログ出力（パスワードは除く）
    print(f"DB接続URL: mysql+pymysql://{DB_USER}:***@/{DB_NAME}?unix_socket={socket_path}")
else:
    # ローカル開発環境では直接接続
    db_url = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    print(f"DB接続URL: mysql+pymysql://{DB_USER}:***@{DB_HOST}:{DB_PORT}/{DB_NAME}")

# データベースエンジンの作成
engine = create_engine(
    db_url, 
    pool_recycle=90, 
    pool_timeout=30,
    pool_pre_ping=True
)

# セッションの作成
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# モデルのベースクラス
Base = declarative_base()

# 要約データモデル
class VideoSummary(Base):
    __tablename__ = "video_summaries"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String(255), nullable=False, index=True)
    video_title = Column(String(500))
    video_description = Column(Text)
    channel_title = Column(String(255))
    channel_id = Column(String(255))
    sub_title = Column(String(500))
    overview = Column(Text)
    main_topics = Column(JSON)  # MySQLではARRAYタイプがないためJSONを使用
    keywords = Column(JSON)     # MySQLではARRAYタイプがないためJSONを使用
    action_items = Column(JSON) # MySQLではARRAYタイプがないためJSONを使用
    key_points = Column(JSON)   # 構造化データは保持
    gcs_path = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<VideoSummary(video_id='{self.video_id}', title='{self.video_title}')>"

# データベーステーブルの作成
def create_tables():
    Base.metadata.create_all(bind=engine)
    print("データベーステーブル作成成功")
