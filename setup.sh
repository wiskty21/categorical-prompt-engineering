#!/bin/bash
# 圏論的プロンプトエンジニアリング セットアップスクリプト

set -e  # エラー時に停止

echo "🚀 圏論的プロンプトエンジニアリング セットアップ開始"
echo "=================================================="

# 色付きメッセージ用関数
print_info() {
    echo -e "\033[1;34mℹ️  $1\033[0m"
}

print_success() {
    echo -e "\033[1;32m✅ $1\033[0m"
}

print_warning() {
    echo -e "\033[1;33m⚠️  $1\033[0m"
}

print_error() {
    echo -e "\033[1;31m❌ $1\033[0m"
}

# 必要なディレクトリ作成
print_info "必要なディレクトリを作成中..."
mkdir -p data logs config notebooks

# .envファイルの確認・作成
if [ ! -f .env ]; then
    print_warning ".envファイルが見つかりません。テンプレートを作成します。"
    cat > .env << EOL
# 圏論的プロンプトエンジニアリング 環境設定

# Claude API設定（必須）
CLAUDE_API_KEY=your_api_key_here

# 環境設定
CATEGORICAL_ENV=development
LOG_LEVEL=INFO

# ポート設定
API_PORT=8000
DEMO_PORT=8501
JUPYTER_PORT=8888
REDIS_PORT=6379

# キャッシュ設定
USE_REDIS_CACHE=true
CACHE_TTL=3600

# セキュリティ設定
SECRET_KEY=change_this_secret_key
DEBUG=false
EOL
    print_warning ".envファイルを作成しました。CLAUDE_API_KEYを設定してください。"
else
    print_success ".envファイルが存在します。"
fi

# API キーの確認
if ! grep -q "your_api_key_here" .env 2>/dev/null; then
    print_success "CLAUDE_API_KEYが設定されているようです。"
else
    print_error "CLAUDE_API_KEYが設定されていません！"
    print_info "以下のいずれかの方法でAPIキーを設定してください："
    echo "  1. .envファイルを編集: CLAUDE_API_KEY=your_actual_api_key"
    echo "  2. 環境変数を設定: export CLAUDE_API_KEY=your_actual_api_key"
    echo ""
fi

# Python 環境の確認
print_info "Python環境を確認中..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    print_success "Python ${PYTHON_VERSION} が見つかりました。"
    
    # 仮想環境の作成・アクティベート
    if [ ! -d "venv" ]; then
        print_info "Python仮想環境を作成中..."
        python3 -m venv venv
    fi
    
    print_info "仮想環境をアクティベート中..."
    source venv/bin/activate
    
    # パッケージのインストール
    print_info "必要なパッケージをインストール中..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    print_success "Pythonパッケージのインストール完了。"
else
    print_error "Python3 が見つかりません。Python 3.8以上をインストールしてください。"
fi

# Docker環境の確認
print_info "Docker環境を確認中..."
if command -v docker &> /dev/null; then
    print_success "Docker が見つかりました。"
    
    if command -v docker-compose &> /dev/null || docker compose version &> /dev/null; then
        print_success "Docker Compose が利用可能です。"
        
        # Dockerイメージのビルド確認
        print_info "Dockerイメージをビルドしますか？ (y/N)"
        read -r response
        if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
            print_info "Dockerイメージをビルド中..."
            docker-compose build
            print_success "Dockerイメージのビルド完了。"
        fi
    else
        print_warning "Docker Compose が見つかりません。Docker Compose をインストールすることを推奨します。"
    fi
else
    print_warning "Docker が見つかりません。Docker環境での実行にはDockerのインストールが必要です。"
fi

# 権限設定
print_info "実行権限を設定中..."
chmod +x categorical_cli.py
chmod +x setup.sh

# テスト実行
print_info "基本動作テストを実行中..."
if source venv/bin/activate && python categorical_cli.py --help &> /dev/null; then
    print_success "CLI ツールが正常に動作します。"
else
    print_warning "CLI ツールの動作確認でエラーが発生しました。依存関係を確認してください。"
fi

# 使用方法の表示
echo ""
echo "=================================================="
print_success "セットアップ完了！"
echo "=================================================="
echo ""
echo "🚀 使用方法:"
echo ""
echo "【Python環境での直接実行】"
echo "  source venv/bin/activate  # 仮想環境アクティベート"
echo "  python categorical_cli.py --help"
echo "  python categorical_cli.py interactive"
echo ""
echo "【Docker環境での実行】"
echo "  docker-compose up -d  # サービス起動"
echo "  docker-compose run categorical-prompt --help"
echo "  docker-compose run categorical-prompt interactive"
echo ""
echo "【Webデモサイト】"
echo "  docker-compose up categorical-demo"
echo "  ブラウザで http://localhost:8501 にアクセス"
echo ""
echo "【Jupyter Notebook】"
echo "  docker-compose up categorical-jupyter"
echo "  ブラウザで http://localhost:8888 にアクセス"
echo ""
echo "🔧 設定ファイル:"
echo "  - CLI設定: cli_config.yaml"
echo "  - 環境設定: .env"
echo "  - バッチ処理: batch_config_sample.json"
echo ""
print_warning "重要: .envファイルでCLAUDE_API_KEYを設定することを忘れないでください！"