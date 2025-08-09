#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
圏論的プロンプトエンジニアリング CLI ツール

コマンドライン操作による自動化とバッチ処理を提供
開発者・研究者向けの効率的なワークフロー支援

Usage:
    categorical_cli.py tensor --input "テキスト" --perspectives "観点1,観点2,観点3"
    categorical_cli.py transform --source "技術文書" --target "初心者向け" --text "内容"
    categorical_cli.py adjoint --input "制約条件" --cycle
    categorical_cli.py monad --context "初期文脈" --develop "新しい入力"
    categorical_cli.py batch --config config.json
    categorical_cli.py interactive
"""

import argparse
import asyncio
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml
import logging
from datetime import datetime
import colorama
from colorama import Fore, Back, Style

# 自作モジュールのインポート
try:
    import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from optimized_categorical_prompt import (
        OptimizedTensorProduct, OptimizedClaudeClient, OptimizationConfig
    )
    import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from async_categorical_prompt import (
        AsyncNaturalTransformation, AsyncAdjointPair, AsyncContextMonad
    )
    import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from robust_categorical_prompt import RobustConfig
except ImportError as e:
    print(f"❌ 必要なモジュールが見つかりません: {e}")
    print("optimized_categorical_prompt.py と async_categorical_prompt.py が必要です")
    sys.exit(1)

# カラー出力の初期化
colorama.init()

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CLIConfig:
    """CLI設定管理"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or "cli_config.yaml"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """設定ファイル読み込み"""
        if Path(self.config_path).exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logger.warning(f"設定ファイル読み込みエラー: {e}")
        
        return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """デフォルト設定"""
        return {
            "api": {
                "claude_model": "claude-3-haiku-20240307",
                "max_tokens": 1000,
                "timeout": 30
            },
            "optimization": {
                "use_cache": True,
                "use_batch": True,
                "max_concurrent": 5
            },
            "output": {
                "format": "json",  # json, yaml, text
                "verbose": True,
                "color": True
            },
            "perspectives": {
                "default": ["技術", "ビジネス", "ユーザー", "セキュリティ"]
            }
        }
    
    def save_config(self):
        """設定ファイル保存"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
            print(f"✅ 設定を保存しました: {self.config_path}")
        except Exception as e:
            print(f"❌ 設定保存エラー: {e}")


class OutputFormatter:
    """出力フォーマッタ"""
    
    def __init__(self, format_type: str = "json", use_color: bool = True):
        self.format_type = format_type.lower()
        self.use_color = use_color
    
    def format_result(self, result: Dict[str, Any], operation: str) -> str:
        """結果をフォーマット"""
        if self.format_type == "json":
            return self._format_json(result, operation)
        elif self.format_type == "yaml":
            return self._format_yaml(result, operation)
        else:
            return self._format_text(result, operation)
    
    def _format_json(self, result: Dict[str, Any], operation: str) -> str:
        """JSON形式でフォーマット"""
        return json.dumps({
            "operation": operation,
            "timestamp": datetime.now().isoformat(),
            "result": result
        }, ensure_ascii=False, indent=2)
    
    def _format_yaml(self, result: Dict[str, Any], operation: str) -> str:
        """YAML形式でフォーマット"""
        data = {
            "operation": operation,
            "timestamp": datetime.now().isoformat(),
            "result": result
        }
        return yaml.dump(data, allow_unicode=True, default_flow_style=False)
    
    def _format_text(self, result: Dict[str, Any], operation: str) -> str:
        """テキスト形式でフォーマット"""
        output = []
        
        if self.use_color:
            output.append(f"{Fore.CYAN}📋 {operation.upper()} 結果{Style.RESET_ALL}")
        else:
            output.append(f"📋 {operation.upper()} 結果")
        
        output.append("=" * 60)
        
        # 処理時間
        if "processing_time" in result:
            if self.use_color:
                output.append(f"{Fore.GREEN}⏱️  処理時間: {result['processing_time']:.2f}秒{Style.RESET_ALL}")
            else:
                output.append(f"⏱️  処理時間: {result['processing_time']:.2f}秒")
        
        # メイン結果
        if "integrated_result" in result:
            output.append("\n🎯 統合結果:")
            output.append("-" * 30)
            output.append(result["integrated_result"])
        
        elif "transformed_content" in result:
            output.append("\n🔄 変換結果:")
            output.append("-" * 30)
            output.append(result["transformed_content"])
        
        elif "evolved_context" in result:
            output.append("\n🧠 発展した文脈:")
            output.append("-" * 30)
            output.append(result["evolved_context"])
        
        # 個別結果
        if "individual_results" in result:
            output.append("\n🔍 個別分析:")
            for perspective, analysis in result["individual_results"].items():
                output.append(f"\n【{perspective}】")
                preview = analysis[:200] + "..." if len(analysis) > 200 else analysis
                output.append(preview)
        
        # 最適化統計
        if "optimization_stats" in result and result["optimization_stats"]:
            output.append(f"\n📊 最適化統計:")
            stats = result["optimization_stats"]
            
            if "cache_stats" in stats:
                cache = stats["cache_stats"]
                output.append(f"  キャッシュ: {cache.get('hit_rate', 0):.1%} ヒット率")
            
            if "performance_stats" in stats:
                output.append(f"  パフォーマンス: 監視中")
        
        return "\n".join(output)
    
    def print_error(self, error: str, operation: str = ""):
        """エラー出力"""
        if self.use_color:
            print(f"{Fore.RED}❌ エラー{(' [' + operation + ']') if operation else ''}: {error}{Style.RESET_ALL}")
        else:
            print(f"❌ エラー{(' [' + operation + ']') if operation else ''}: {error}")
    
    def print_info(self, message: str):
        """情報出力"""
        if self.use_color:
            print(f"{Fore.BLUE}ℹ️  {message}{Style.RESET_ALL}")
        else:
            print(f"ℹ️  {message}")
    
    def print_success(self, message: str):
        """成功出力"""
        if self.use_color:
            print(f"{Fore.GREEN}✅ {message}{Style.RESET_ALL}")
        else:
            print(f"✅ {message}")


class CategoricalCLI:
    """圏論的プロンプトエンジニアリング CLI"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.cli_config = CLIConfig(config_path)
        self.formatter = OutputFormatter(
            self.cli_config.config["output"]["format"],
            self.cli_config.config["output"]["color"]
        )
        
        # 最適化された圏論クライアント
        optimization_config = OptimizationConfig()
        optimization_config.max_concurrent_requests = self.cli_config.config["optimization"]["max_concurrent"]
        
        self.client = None  # 実際の使用時に初期化
        self.tensor_product = None
        self.natural_transformation = None
        self.adjoint_pair = None
        self.context_monad = None
    
    async def _ensure_client(self):
        """クライアント初期化（遅延初期化）"""
        if self.client is None:
            optimization_config = OptimizationConfig()
            api_key = os.getenv("CLAUDE_API_KEY")
            
            if not api_key:
                raise ValueError("CLAUDE_API_KEY が設定されていません")
            
            self.client = OptimizedClaudeClient(api_key, optimization_config)
    
    async def tensor_operation(self, input_text: str, perspectives: List[str], 
                             use_cache: bool = True, use_batch: bool = True) -> Dict[str, Any]:
        """テンソル積操作"""
        await self._ensure_client()
        
        if not perspectives:
            perspectives = self.cli_config.config["perspectives"]["default"]
        
        self.formatter.print_info(f"テンソル積実行: {len(perspectives)}個の観点で分析")
        
        tensor = OptimizedTensorProduct(perspectives, client=self.client)
        result = await tensor.apply(input_text, use_cache, use_batch)
        
        return result
    
    async def natural_transformation(self, source_domain: str, target_domain: str, 
                                   content: str, transformation_rule: str = None) -> Dict[str, Any]:
        """自然変換操作"""
        await self._ensure_client()
        
        if not transformation_rule:
            transformation_rule = f"{source_domain}から{target_domain}への適切な変換"
        
        self.formatter.print_info(f"自然変換実行: {source_domain} → {target_domain}")
        
        transformer = AsyncNaturalTransformation(source_domain, target_domain, transformation_rule)
        result = await transformer.apply_transformation(content)
        
        return result
    
    async def adjoint_operation(self, input_text: str, cycle: bool = False) -> Dict[str, Any]:
        """アジョイント関手操作"""
        self.formatter.print_info(f"アジョイント関手実行 (サイクル: {cycle})")
        
        adjoint = AsyncAdjointPair()
        
        if cycle:
            result = await adjoint.adjoint_cycle(input_text)
        else:
            result = await adjoint.free_construction(input_text)
        
        return result
    
    async def monad_operation(self, initial_context: str, developments: List[str]) -> Dict[str, Any]:
        """モナド操作"""
        self.formatter.print_info(f"モナド発展実行: {len(developments)}段階")
        
        monad = AsyncContextMonad(initial_context)
        results = []
        
        for i, development in enumerate(developments, 1):
            self.formatter.print_info(f"段階 {i}: {development}")
            result = await monad.bind(development)
            results.append(result)
        
        return {
            "initial_context": initial_context,
            "developments": developments,
            "results": results,
            "final_context": monad.current_context
        }
    
    async def batch_process(self, batch_config: Dict[str, Any]) -> Dict[str, Any]:
        """バッチ処理"""
        self.formatter.print_info("バッチ処理実行中...")
        
        results = []
        
        for task in batch_config.get("tasks", []):
            operation = task.get("operation")
            params = task.get("parameters", {})
            
            try:
                if operation == "tensor":
                    result = await self.tensor_operation(**params)
                elif operation == "transform":
                    result = await self.natural_transformation(**params)
                elif operation == "adjoint":
                    result = await self.adjoint_operation(**params)
                elif operation == "monad":
                    result = await self.monad_operation(**params)
                else:
                    result = {"error": f"不明な操作: {operation}"}
                
                results.append({
                    "operation": operation,
                    "parameters": params,
                    "result": result
                })
                
            except Exception as e:
                results.append({
                    "operation": operation,
                    "parameters": params,
                    "error": str(e)
                })
        
        return {"batch_results": results}
    
    def interactive_mode(self):
        """インタラクティブモード"""
        print(f"{Fore.MAGENTA}🚀 圏論的プロンプトエンジニアリング インタラクティブモード{Style.RESET_ALL}")
        print("使用可能なコマンド: tensor, transform, adjoint, monad, config, exit")
        
        while True:
            try:
                command = input(f"{Fore.CYAN}categorical> {Style.RESET_ALL}").strip()
                
                if command in ["exit", "quit", "q"]:
                    print("👋 お疲れ様でした！")
                    break
                
                elif command == "help":
                    self._show_interactive_help()
                
                elif command == "config":
                    self._show_config()
                
                elif command.startswith("tensor"):
                    self._interactive_tensor(command)
                
                elif command.startswith("transform"):
                    self._interactive_transform(command)
                
                elif command.startswith("adjoint"):
                    self._interactive_adjoint(command)
                
                elif command.startswith("monad"):
                    self._interactive_monad(command)
                
                else:
                    print("❓ 不明なコマンドです。'help' で使用方法を確認してください。")
            
            except KeyboardInterrupt:
                print("\n👋 お疲れ様でした！")
                break
            except Exception as e:
                self.formatter.print_error(str(e), "interactive")
    
    def _show_interactive_help(self):
        """インタラクティブヘルプ"""
        help_text = """
📖 圏論的プロンプトエンジニアリング CLI ヘルプ

🔹 基本コマンド:
  tensor <入力テキスト>        - テンソル積による多角的分析
  transform <内容>            - 自然変換による領域変換
  adjoint <入力>              - アジョイント関手による双対処理
  monad <初期文脈>            - モナドによる文脈発展
  
🔹 システムコマンド:
  config                     - 現在の設定表示
  help                       - このヘルプ表示
  exit/quit/q               - 終了

🔹 使用例:
  tensor 人工知能の未来について考える
  transform この技術文書を初心者向けに変換
  adjoint 効率化の制約条件
  monad プロジェクトの企画段階
"""
        print(help_text)
    
    def _show_config(self):
        """設定表示"""
        print("⚙️  現在の設定:")
        config_yaml = yaml.dump(self.cli_config.config, allow_unicode=True, default_flow_style=False)
        print(config_yaml)
    
    def _interactive_tensor(self, command: str):
        """インタラクティブテンソル積"""
        parts = command.split(" ", 1)
        if len(parts) < 2:
            print("使用法: tensor <分析対象テキスト>")
            return
        
        input_text = parts[1]
        
        # 非同期実行
        result = asyncio.run(self.tensor_operation(input_text, []))
        output = self.formatter.format_result(result, "tensor")
        print(output)
    
    def _interactive_transform(self, command: str):
        """インタラクティブ自然変換"""
        parts = command.split(" ", 1)
        if len(parts) < 2:
            print("使用法: transform <変換対象テキスト>")
            return
        
        content = parts[1]
        source = input("変換元領域: ").strip() or "一般文書"
        target = input("変換先領域: ").strip() or "分かりやすい説明"
        
        result = asyncio.run(self.natural_transformation(source, target, content))
        output = self.formatter.format_result(result, "transform")
        print(output)
    
    def _interactive_adjoint(self, command: str):
        """インタラクティブアジョイント関手"""
        parts = command.split(" ", 1)
        if len(parts) < 2:
            print("使用法: adjoint <入力テキスト>")
            return
        
        input_text = parts[1]
        cycle = input("サイクル実行しますか？ (y/N): ").strip().lower() == 'y'
        
        result = asyncio.run(self.adjoint_operation(input_text, cycle))
        output = self.formatter.format_result(result, "adjoint")
        print(output)
    
    def _interactive_monad(self, command: str):
        """インタラクティブモナド"""
        parts = command.split(" ", 1)
        if len(parts) < 2:
            print("使用法: monad <初期文脈>")
            return
        
        initial_context = parts[1]
        developments = []
        
        print("発展させる内容を入力してください（空行で終了）:")
        while True:
            dev = input("  発展内容: ").strip()
            if not dev:
                break
            developments.append(dev)
        
        if developments:
            result = asyncio.run(self.monad_operation(initial_context, developments))
            output = self.formatter.format_result(result, "monad")
            print(output)
        else:
            print("発展内容が入力されませんでした。")
    
    async def cleanup(self):
        """リソースクリーンアップ"""
        if self.client:
            await self.client.cleanup()


def create_parser() -> argparse.ArgumentParser:
    """コマンドライン引数パーサー作成"""
    parser = argparse.ArgumentParser(
        description="圏論的プロンプトエンジニアリング CLI ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  %(prog)s tensor --input "AI技術の発展" --perspectives "技術,社会,経済"
  %(prog)s transform --source "技術文書" --target "初心者向け" --content "機械学習について"
  %(prog)s adjoint --input "制約条件" --cycle
  %(prog)s monad --context "プロジェクト開始" --develop "要件定義" --develop "設計"
  %(prog)s batch --config batch_config.json
  %(prog)s interactive
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="使用可能なコマンド")
    
    # tensor コマンド
    tensor_parser = subparsers.add_parser("tensor", help="テンソル積による多角的分析")
    tensor_parser.add_argument("--input", "-i", required=True, help="分析対象テキスト")
    tensor_parser.add_argument("--perspectives", "-p", help="観点リスト（カンマ区切り）")
    tensor_parser.add_argument("--no-cache", action="store_true", help="キャッシュを無効化")
    tensor_parser.add_argument("--no-batch", action="store_true", help="バッチ処理を無効化")
    
    # transform コマンド
    transform_parser = subparsers.add_parser("transform", help="自然変換による領域変換")
    transform_parser.add_argument("--source", "-s", required=True, help="変換元領域")
    transform_parser.add_argument("--target", "-t", required=True, help="変換先領域")
    transform_parser.add_argument("--content", "-c", required=True, help="変換対象内容")
    transform_parser.add_argument("--rule", "-r", help="変換ルール")
    
    # adjoint コマンド  
    adjoint_parser = subparsers.add_parser("adjoint", help="アジョイント関手による双対処理")
    adjoint_parser.add_argument("--input", "-i", required=True, help="入力テキスト")
    adjoint_parser.add_argument("--cycle", action="store_true", help="サイクル実行")
    
    # monad コマンド
    monad_parser = subparsers.add_parser("monad", help="モナドによる文脈発展")
    monad_parser.add_argument("--context", "-c", required=True, help="初期文脈")
    monad_parser.add_argument("--develop", "-d", action="append", help="発展内容（複数指定可能）")
    
    # batch コマンド
    batch_parser = subparsers.add_parser("batch", help="バッチ処理実行")
    batch_parser.add_argument("--config", "-c", required=True, help="バッチ設定ファイル")
    
    # interactive コマンド
    interactive_parser = subparsers.add_parser("interactive", help="インタラクティブモード")
    
    # 共通オプション
    parser.add_argument("--config-file", help="CLI設定ファイル")
    parser.add_argument("--output", "-o", choices=["json", "yaml", "text"], help="出力形式")
    parser.add_argument("--no-color", action="store_true", help="カラー出力を無効化")
    parser.add_argument("--verbose", "-v", action="store_true", help="詳細出力")
    parser.add_argument("--quiet", "-q", action="store_true", help="静寂モード")
    
    return parser


async def main():
    """メイン関数"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # CLI初期化
    cli = CategoricalCLI(args.config_file)
    
    # 出力設定の調整
    if args.output:
        cli.cli_config.config["output"]["format"] = args.output
    if args.no_color:
        cli.cli_config.config["output"]["color"] = False
    if args.verbose:
        cli.cli_config.config["output"]["verbose"] = True
    elif args.quiet:
        cli.cli_config.config["output"]["verbose"] = False
    
    # フォーマッタ更新
    cli.formatter = OutputFormatter(
        cli.cli_config.config["output"]["format"],
        cli.cli_config.config["output"]["color"]
    )
    
    try:
        if args.command == "tensor":
            perspectives = args.perspectives.split(",") if args.perspectives else None
            result = await cli.tensor_operation(
                args.input, 
                perspectives,
                not args.no_cache,
                not args.no_batch
            )
            output = cli.formatter.format_result(result, "tensor")
            print(output)
        
        elif args.command == "transform":
            result = await cli.natural_transformation(
                args.source, args.target, args.content, args.rule
            )
            output = cli.formatter.format_result(result, "transform")
            print(output)
        
        elif args.command == "adjoint":
            result = await cli.adjoint_operation(args.input, args.cycle)
            output = cli.formatter.format_result(result, "adjoint")
            print(output)
        
        elif args.command == "monad":
            developments = args.develop or []
            result = await cli.monad_operation(args.context, developments)
            output = cli.formatter.format_result(result, "monad")
            print(output)
        
        elif args.command == "batch":
            try:
                with open(args.config, 'r', encoding='utf-8') as f:
                    batch_config = json.load(f)
                
                result = await cli.batch_process(batch_config)
                output = cli.formatter.format_result(result, "batch")
                print(output)
                
            except FileNotFoundError:
                cli.formatter.print_error(f"バッチ設定ファイルが見つかりません: {args.config}")
            except json.JSONDecodeError as e:
                cli.formatter.print_error(f"バッチ設定ファイルの形式エラー: {e}")
        
        elif args.command == "interactive":
            cli.interactive_mode()
        
    except Exception as e:
        cli.formatter.print_error(str(e), args.command)
        
    finally:
        await cli.cleanup()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 処理を中断しました")
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        sys.exit(1)