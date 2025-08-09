# 🚀 圏論的プロンプトエンジニアリング セットアップガイド

## 📋 クイックスタート（最短5分）

### ⚡ 1. 環境準備
```bash
# リポジトリクローン
git clone https://github.com/wiskty21/categorical-prompt-engineering.git
cd categorical-prompt-engineering

# 仮想環境作成・有効化
python -m venv venv
source venv/bin/activate  # Mac/Linux
# venv\Scripts\activate    # Windows
```

### 🔑 2. API キー設定
```bash
# Claude API キーを設定
echo "CLAUDE_API_KEY=your-api-key-here" > .env
```

**Claude API キーの取得方法:**
1. https://console.anthropic.com にアクセス
2. アカウント作成・ログイン  
3. API Keys → Create Key
4. 生成されたキーを上記の`your-api-key-here`に置き換え

### 📦 3. 依存関係インストール
```bash
# 全パッケージ一括インストール
pip install -r infrastructure/requirements.txt

# 確認
pip list | grep -E "(anthropic|streamlit|plotly|fastapi)"
```

### ✅ 4. 動作確認
```bash
# 最も簡単なテスト
python src/demos/live_demo.py

# Web UI デモ
streamlit run src/interfaces/categorical_demo.py
```

---

## 🛠️ 詳細セットアップ

### 🐍 Python環境要件
- **Python**: 3.10+ (推奨: 3.10.x)
- **OS**: Windows 10+, macOS 12+, Ubuntu 20.04+
- **メモリ**: 4GB+ (8GB推奨)
- **ストレージ**: 2GB+ 空き容量

### 📚 依存関係詳細

#### Core Dependencies
```bash
# 必須パッケージ（絶対必要）
pip install anthropic>=0.20.0 python-dotenv>=1.0.0 aiohttp>=3.8.0
```

#### Web UI Dependencies  
```bash
# Streamlit Webデモ用
pip install streamlit>=1.28.0 plotly>=5.17.0 pandas>=2.0.0
```

#### API Server Dependencies
```bash  
# FastAPI サーバー用
pip install fastapi>=0.100.0 uvicorn[standard]>=0.20.0
```

#### Development Dependencies
```bash
# 開発・テスト用
pip install pytest>=7.0.0 pytest-asyncio>=0.21.0
```

### 🔧 環境別インストール

#### Mac (Homebrew使用)
```bash
# Python 3.10インストール
brew install python@3.10

# 仮想環境作成
python3.10 -m venv venv
source venv/bin/activate

# パッケージインストール
pip install -r infrastructure/requirements.txt
```

#### Ubuntu/Debian
```bash
# Python 3.10インストール  
sudo apt update
sudo apt install python3.10 python3.10-venv python3.10-dev

# 仮想環境作成
python3.10 -m venv venv
source venv/bin/activate

# パッケージインストール
pip install -r infrastructure/requirements.txt
```

#### Windows
```powershell
# Python 3.10 (Microsoft Store推奨)
# または https://python.org からダウンロード

# 仮想環境作成
python -m venv venv
venv\Scripts\activate

# パッケージインストール
pip install -r infrastructure/requirements.txt
```

---

## 🐳 Docker セットアップ（推奨）

### 基本Docker実行
```bash
# Docker イメージビルド
docker build -f infrastructure/Dockerfile -t categorical-prompt .

# コンテナ実行
docker run -e CLAUDE_API_KEY=your-key -p 8501:8501 categorical-prompt
```

### Docker Compose（全サービス）
```bash
# 環境設定
echo "CLAUDE_API_KEY=your-key" > .env

# 全サービス起動
docker-compose -f infrastructure/docker-compose.yml up -d

# アクセス
# Web UI: http://localhost:8501
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

---

## 🔍 動作確認・テスト

### ✅ 基本機能テスト
```bash
# 1. API接続テスト
python src/tests/test_api_connection.py

# 2. ライブデモ
python src/demos/live_demo.py

# 3. 統合シナリオテスト  
python src/demos/integrated_demo.py
```

### 🌐 Web インターフェース
```bash  
# Streamlit Web UI
streamlit run src/interfaces/categorical_demo.py
# → http://localhost:8501

# FastAPI サーバー
python src/interfaces/categorical_api.py  
# → http://localhost:8000/docs
```

### 🖥️ CLI インターフェース
```bash
# インタラクティブモード
python src/interfaces/categorical_cli.py interactive

# 直接実行
python src/interfaces/categorical_cli.py tensor --input "AI分析" --perspectives "技術,市場,社会"
```

---

## ❗ トラブルシューティング

### よくある問題と解決法

#### 1. `ModuleNotFoundError`
```bash
# パスの問題 → 仮想環境確認
which python
pip list

# 不足パッケージ → 再インストール
pip install -r infrastructure/requirements.txt
```

#### 2. `anthropic.APIError`  
```bash
# APIキー確認
cat .env
echo $CLAUDE_API_KEY

# APIキー再設定
export CLAUDE_API_KEY=your-correct-key
```

#### 3. Streamlit起動エラー
```bash
# ポート競合 → 別ポート使用
streamlit run src/interfaces/categorical_demo.py --server.port 8502

# 権限問題 → ユーザー権限確認
ls -la src/interfaces/categorical_demo.py
```

#### 4. Docker エラー
```bash
# Docker起動確認
docker version
docker-compose version

# イメージ再ビルド
docker-compose down
docker-compose build --no-cache
docker-compose up
```

### デバッグモード
```bash
# 詳細ログ出力
export PYTHONPATH=$PWD/src/core
export DEBUG=true

python src/demos/live_demo.py
```

---

## 🌟 推奨セットアップ（初心者向け）

### Step 1: 最小構成
```bash  
git clone https://github.com/wiskty21/categorical-prompt-engineering.git
cd categorical-prompt-engineering
python -m venv venv
source venv/bin/activate  # Mac/Linux
pip install anthropic python-dotenv
echo "CLAUDE_API_KEY=your-key" > .env
```

### Step 2: 動作確認
```bash
python -c "
import sys
sys.path.append('src/core')
from async_categorical_prompt import AsyncTensorProduct
print('✅ 基本動作OK')
"
```

### Step 3: フル機能
```bash
pip install -r infrastructure/requirements.txt
python src/demos/live_demo.py
```

---

## 🔗 次のステップ

### 📚 学習リソース  
- **初心者**: `docs/guides/圏論的プロンプトエンジニアリング_高校生向け解説.md`
- **開発者**: `PROJECT_SUMMARY.md`  
- **研究者**: `docs/reports/academic_paper_draft.md`

### 🚀 実用化
- **ビジネス**: `docs/reports/enterprise_service_analysis.md`
- **教育**: `docs/reports/education_curriculum.md`
- **コミュニティ**: `docs/reports/community_development_plan.md`

### 🤝 貢献・質問
- **GitHub Issues**: バグ報告・機能要求
- **Discussions**: 質問・議論・アイデア
- **Pull Requests**: コード貢献・改善提案

---

**🎉 セットアップ完了！圏論的プロンプトエンジニアリングの世界をお楽しみください！** ✨