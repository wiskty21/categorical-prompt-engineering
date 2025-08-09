# 圏論的プロンプトエンジニアリング Docker イメージ
FROM python:3.11-slim

# メタデータ
LABEL maintainer="Categorical Prompt Engineering Team"
LABEL description="圏論的プロンプトエンジニアリング実行環境"
LABEL version="1.0"

# 環境変数
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONPATH=/app

# 作業ディレクトリ設定
WORKDIR /app

# システム依存パッケージのインストール
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 必要なPythonパッケージのインストール用requirements.txt作成
COPY requirements.txt .

# Pythonパッケージインストール
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# アプリケーションファイルのコピー
COPY *.py ./
COPY *.yaml ./
COPY *.json ./
COPY *.md ./

# CLI実行権限付与
RUN chmod +x categorical_cli.py

# 非rootユーザー作成と設定
RUN useradd --create-home --shell /bin/bash categorical && \
    chown -R categorical:categorical /app

USER categorical

# ヘルスチェック
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import sys; sys.exit(0)"

# デフォルトポート（Webサーバー用）
EXPOSE 8000

# デフォルトエントリポイント
ENTRYPOINT ["python", "categorical_cli.py"]

# デフォルトコマンド（ヘルプ表示）
CMD ["--help"]