# ベースイメージとしてPython 3.12.9-slimを使用
FROM python:3.12.9-slim

# 作業ディレクトリの設定
WORKDIR /app

# 必要なシステムパッケージのインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 環境変数の設定
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# 依存関係ファイルのコピーと必要なパッケージのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# インストールされたパッケージの一覧をビルドログに出力
RUN pip list

# アプリケーションコードのコピー
COPY . .

# ポートの公開
EXPOSE 8000

# ヘルスチェック用のスクリプトを作成
RUN echo '#!/bin/bash\n\
echo "Starting health check script..."\n\
if ! nc -z localhost $PORT; then\n\
  echo "Error: Application is not listening on port $PORT"\n\
  exit 1\n\
fi\n\
echo "Health check passed: Application is listening on port $PORT"\n\
exit 0' > /app/healthcheck.sh && chmod +x /app/healthcheck.sh

# 起動スクリプトを作成
RUN echo '#!/bin/bash\n\
echo "Starting application..."\n\
echo "Environment: $K_SERVICE"\n\
echo "Cloud SQL Connection: $INSTANCE_CONNECTION_NAME"\n\
echo "DB Host: $DB_HOST"\n\
echo "DB Port: $DB_PORT"\n\
echo "DB User: $DB_USER"\n\
# データベース接続エラーがあってもアプリケーションを起動する\n\
python main.py' > /app/start.sh && chmod +x /app/start.sh

# アプリケーションの実行
CMD ["/app/start.sh"]