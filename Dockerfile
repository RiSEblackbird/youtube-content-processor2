# ベースイメージとしてPython 3.12.9-slimを使用
FROM python:3.12.9-slim

# 作業ディレクトリの設定
WORKDIR /app

# 必要なシステムパッケージのインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
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

# アプリケーションの実行
CMD ["python", "main.py"]