from google.cloud import storage
from google.api_core import exceptions
import os
from dotenv import load_dotenv

def check_permissions():
    load_dotenv()
    bucket_name = os.getenv('GCS_BUCKET_NAME')
    
    print(f"GCS権限チェックを実行中...\n")
    
    try:
        # クライアントの初期化
        client = storage.Client()
        credentials = client._credentials
        service_account_email = credentials.service_account_email
        print(f"サービスアカウント: {service_account_email}\n")
        
        print("1. バケットの存在確認")
        try:
            # バケットの一覧取得を試行
            buckets = list(client.list_buckets(max_results=1))
            print("✓ バケット一覧の取得に成功")
        except exceptions.Forbidden:
            print("❌ バケット一覧の取得に失敗 - storage.buckets.list 権限なし（=> 必須じゃなかった。）")
        
        print("\n2. 指定バケットへのアクセス確認")
        try:
            bucket = client.get_bucket(bucket_name)
            print(f"✓ バケット '{bucket_name}' へのアクセスに成功")
        except exceptions.Forbidden:
            print(f"❌ バケット '{bucket_name}' へのアクセスに失敗 - storage.buckets.get 権限が必要です")
            print("\n必要な権限:")
            print("- バケットレベル:")
            print("  * roles/storage.objectViewer")
            print("  * roles/storage.objectCreator")
            print("  * roles/storage.buckets.get")
            return
        except exceptions.NotFound:
            print(f"❌ バケット '{bucket_name}' が存在しません")
            return
        
        print("\n3. オブジェクト操作の確認")
        try:
            # テストファイルの作成を試行
            blob = bucket.blob('_test_permissions.txt')
            blob.upload_from_string('テスト', content_type='text/plain')
            print("✓ オブジェクトの作成に成功")
            
            # テストファイルの読み取りを試行
            blob.download_as_string()
            print("✓ オブジェクトの読み取りに成功")
            
            # テストファイルの削除を試行
            blob.delete()
            print("✓ オブジェクトの削除に成功")
        except exceptions.Forbidden as e:
            print(f"❌ オブジェクト操作に失敗: {str(e)}")
            
    except Exception as e:
        print(f"\n❌ 予期せぬエラーが発生しました: {str(e)}")
    
    print("\n推奨される権限設定:")
    print("1. プロジェクトレベルでサービスアカウントに以下のロールを付与:")
    print("   - Storage オブジェクト閲覧者 (roles/storage.objectViewer)")
    print("   - Storage オブジェクト作成者 (roles/storage.objectCreator)")
    print("\n2. バケットレベルで以下のIAMポリシーを設定:")
    print(f"   プリンシパル: {service_account_email}")
    print("   ロール:")
    print("   - Storage オブジェクト閲覧者 (roles/storage.objectViewer)")
    print("   - Storage オブジェクト作成者 (roles/storage.objectCreator)")

if __name__ == "__main__":
    check_permissions()