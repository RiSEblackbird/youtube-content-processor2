# ベースイメージとしてNode.jsの最新LTSバージョンを使用
FROM node:20-alpine

# 作業ディレクトリを設定
WORKDIR /app

# パッケージマネージャのキャッシュを利用するために先にpackage.jsonとpackage-lock.jsonをコピー
COPY package*.json ./

# 依存関係をインストール
RUN npm ci

# ソースコードをコピー
COPY . .

# TypeScriptのビルドとNext.jsのビルドを実行
RUN npm run build

# 本番環境用のポートを公開
EXPOSE 3000

# コンテナ起動時にNext.jsアプリケーションを起動
CMD ["npm", "start"]
