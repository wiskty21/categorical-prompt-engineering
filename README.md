# 🧮 圏論的プロンプトエンジニアリング (Categorical Prompt Engineering)

世界初の圏論（Category Theory）を活用した革新的プロンプトエンジニアリングシステム。数学的厳密性と実用的価値を両立した、次世代のAI対話システムです。

## 📖 読み始めガイド

### 🎯 まず最初に読むべきファイル

1. **概念を理解したい方**
   - `圏論的プロンプトエンジニアリング_高校生向け解説.md` - 分かりやすい入門解説
   - `CLAUDE.md` - プロジェクトビジョンと計画

2. **すぐに試したい方**
   - `live_demo.py` - 実際のデモを体験
   - `integrated_demo.py` - 実用シナリオのデモ

3. **開発者の方**
   - `PROJECT_SUMMARY.md` - プロジェクト全体像
   - `async_categorical_prompt.py` - コア実装

## 🗺️ ファイル構成と関係性

```
圏論的プロンプトエンジニアリング/
│
├── 📚 ドキュメント（まず読む）
│   ├── README.md                     # このファイル - 全体案内
│   ├── PROJECT_SUMMARY.md            # プロジェクト概要・統計
│   ├── CLAUDE.md                     # ビジョン・ロードマップ
│   └── 圏論的プロンプトエンジニアリング_高校生向け解説.md  # 入門解説
│
├── 🎯 コア実装（中核となる機能）
│   ├── async_categorical_prompt.py   ⭐ # 非同期圏論実装（メイン）
│   ├── optimized_categorical_prompt.py  # 最適化版
│   └── robust_categorical_prompt.py     # エラー処理強化版
│
├── 🔧 インターフェース（使い方）
│   ├── categorical_cli.py            # CLIツール
│   ├── categorical_demo.py           # Web UI (Streamlit)
│   └── categorical_api.py            # REST API (FastAPI)
│
├── 🧪 デモ・テスト（動作確認）
│   ├── live_demo.py                  # ライブデモ ⭐
│   ├── integrated_demo.py            # 統合シナリオ
│   └── test_categorical_prompt.py    # テストスイート
│
├── 🐳 環境構築
│   ├── Dockerfile                    # メインコンテナ
│   ├── docker-compose.yml            # マルチサービス構成
│   ├── setup.sh                      # セットアップスクリプト
│   └── requirements.txt              # Python依存関係
│
└── 📝 設定ファイル
    ├── .env                          # API キー設定（要作成）
    ├── cli_config.yaml               # CLI設定
    └── batch_config_sample.json      # バッチ処理サンプル
```

## 🚀 クイックスタート

### 1. 環境準備

```bash
# リポジトリクローン
git clone https://github.com/[your-username]/categorical-prompt-engineering.git
cd categorical-prompt-engineering

# 環境構築
python -m venv venv
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

### 2. API キー設定

`.env`ファイルを作成：
```bash
CLAUDE_API_KEY=your-api-key-here
```

### 3. 実行

```bash
# ライブデモ
python live_demo.py

# CLIインタラクティブモード
python categorical_cli.py interactive

# Webデモ
streamlit run categorical_demo.py
```

## 🔬 4つの圏論的操作

### 1. テンソル積 (⊗) - Tensor Product
```python
from async_categorical_prompt import AsyncTensorProduct

tensor = AsyncTensorProduct(["技術", "ビジネス", "社会"])
result = await tensor.apply("AIの未来")
```
**用途**: 複数観点からの並行分析

### 2. 自然変換 - Natural Transformation
```python
from async_categorical_prompt import AsyncNaturalTransformation

transformer = AsyncNaturalTransformation("技術文書", "初心者向け", "平易に変換")
result = await transformer.apply_transformation(content)
```
**用途**: 構造を保った領域変換

### 3. アジョイント関手 - Adjoint Functors
```python
from async_categorical_prompt import AsyncAdjointPair

adjoint = AsyncAdjointPair()
result = await adjoint.free_construction("制約条件")
```
**用途**: 制約からの自由化と本質抽出

### 4. モナド - Monad
```python
from async_categorical_prompt import AsyncContextMonad

monad = AsyncContextMonad("初期文脈")
result = await monad.bind("発展内容")
```
**用途**: 文脈を保持した段階的発展

## 📊 プロジェクト詳細

### 実装規模
- **コード行数**: 7,833行
- **Pythonファイル**: 16個
- **ドキュメント**: 13個
- **テストケース**: 24+

### 技術スタック
- Python 3.10+
- Claude API (Anthropic)
- FastAPI
- Streamlit
- Docker

### パフォーマンス
- テンソル積: 11-12秒（3-4観点並行）
- 自然変換: 2-3秒
- アジョイント: 3-4秒
- モナド: 3-4秒/ステップ

## 📚 詳細ドキュメント

### 開発フェーズ別レポート
- `Phase4_完成レポート.md` - 高度化・最適化の詳細
- `Phase5_エコシステム構築完成レポート.md` - エコシステム構築の詳細

### 実行結果
- `真の圏論実装_動作確認レポート.md` - Claude API連携の動作確認
- `動作確認結果.md` - 基本機能テスト結果

### リソース
- `圏論的プロンプトエンジニアリング_リソース集.md` - 参考文献・論文

## 🛠️ 開発ガイド

### コードの依存関係

```
categorical_prompt_engineering.py (基礎概念)
    ↓
real_categorical_prompt.py (API連携)
    ↓
async_categorical_prompt.py (非同期化) ← メイン実装
    ├→ robust_categorical_prompt.py (エラー処理)
    └→ optimized_categorical_prompt.py (最適化)
         ↓
    CLI / Web UI / REST API
```

### テスト実行

```bash
# 全テスト実行
python test_categorical_prompt.py

# API接続テスト
python test_api_connection.py
```

## 🌟 特徴

- ✅ **世界初**: 圏論的概念をプロンプトエンジニアリングに応用
- ✅ **実用的**: ビジネス・研究・教育での実証済み
- ✅ **高性能**: 非同期並行処理による高速化
- ✅ **堅牢**: プロダクション級エラーハンドリング
- ✅ **完全**: CLI/Web/API/Dockerの全インターフェース

## 🤝 貢献

プルリクエストを歓迎します！詳細は`CLAUDE.md`のPhase 6計画をご覧ください。

## 📜 ライセンス

MIT License

## 🔗 関連情報

- **プロジェクトビジョン**: `CLAUDE.md`
- **技術詳細**: `PROJECT_SUMMARY.md`
- **初心者向け解説**: `圏論的プロンプトエンジニアリング_高校生向け解説.md`

---

**Category Theory meets AI Engineering - Now Reality!** 🚀

*数学の美しさと実用的価値を融合した、革新的なプロンプトエンジニアリングシステム*