from google.cloud import storage
import os
from dotenv import load_dotenv

def test_gcs_credentials():
    # .envファイルの読み込み
    load_dotenv()
    
    print("1. 環境変数の確認")
    credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    bucket_name = os.getenv('GCS_BUCKET_NAME')
    
    if not credentials_path or not bucket_name:
        print("❌ 必要な環境変数が設定されていません")
        print(f"GOOGLE_APPLICATION_CREDENTIALS: {'設定済み' if credentials_path else '未設定'}")
        print(f"GCS_BUCKET_NAME: {'設定済み' if bucket_name else '未設定'}")
        return
    
    print(f"✓ 認証ファイルパス: {credentials_path}")
    print(f"✓ バケット名: {bucket_name}")
    
    print("\n2. 認証ファイルの存在確認")
    if not os.path.exists(credentials_path):
        print(f"❌ 認証ファイルが見つかりません: {credentials_path}")
        return
    print("✓ 認証ファイルが存在します")
    
    print("\n3. GCSクライアントの初期化テスト")
    try:
        client = storage.Client()
        print("✓ GCSクライアントの初期化に成功")
    except Exception as e:
        print(f"❌ GCSクライアントの初期化に失敗: {str(e)}")
        return
    
    print("\n4. バケットへのアクセステスト")
    try:
        bucket = client.bucket(bucket_name)
        # テストファイルの作成を試みる
        blob = bucket.blob('test.txt')
        blob.upload_from_string('テスト成功！', content_type='text/plain')
        print("✓ バケットへのアクセスとファイルのアップロードに成功")
        
        # テストファイルの削除
        blob.delete()
        print("✓ テストファイルの削除に成功")
    except Exception as e:
        print(f"❌ バケットへのアクセスに失敗: {str(e)}")
        return
    
    print("\n✨ すべてのテストが正常に完了しました！")

if __name__ == "__main__":
    test_gcs_credentials()