# API設定ガイド

## Claude API キーの設定方法

### 1. 環境変数ファイルの作成

プロジェクトルートディレクトリに `.env` ファイルを作成してください：

```bash
# .env ファイル
CLAUDE_API_KEY=your_claude_api_key_here
```

### 2. 必要なパッケージのインストール

```bash
pip install python-dotenv anthropic
```

### 3. 実行

```bash
python real_categorical_prompt.py
```

## 重要な注意事項

⚠️ **セキュリティ**
- `.env` ファイルは `.gitignore` に含まれており、Git追跡から除外されています
- APIキーを直接コードに記述しないでください
- 本番環境では適切な環境変数管理システムを使用してください

🔧 **トラブルシューティング**
- `CLAUDE_API_KEY が設定されていません` エラーが出る場合は、`.env` ファイルが正しく作成されているか確認してください
- APIキーが有効であることを確認してください
- ネットワーク接続を確認してください

## ファイル構成

```
.
├── .env                    # APIキー設定（Git追跡外）
├── .gitignore             # Git除外設定
├── real_categorical_prompt.py  # メイン実装
└── README_API_SETUP.md   # この設定ガイド
```