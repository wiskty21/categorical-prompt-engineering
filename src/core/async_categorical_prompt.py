# -*- coding: utf-8 -*-
"""
非同期圏論的プロンプトエンジニアリング実装 - Async版
asyncioによる真の並行処理最適化とパフォーマンス向上

Features:
- 真の非同期並行処理
- 効率的なAPI呼び出し管理
- コネクションプールとレート制限
- エラーハンドリングとリトライ機構
"""

import asyncio
import aiohttp
import anthropic
import time
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json
import os
from dotenv import load_dotenv
import logging

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 環境変数の読み込み
load_dotenv()
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

if not CLAUDE_API_KEY:
    raise ValueError("CLAUDE_API_KEY が設定されていません。.envファイルを確認してください。")


@dataclass
class APIConfig:
    """API設定クラス"""
    max_concurrent_requests: int = 5
    request_timeout: int = 30
    retry_attempts: int = 3
    retry_delay: float = 1.0
    rate_limit_per_minute: int = 50


class AsyncClaudeClient:
    """非同期Claude APIクライアント"""
    
    def __init__(self, api_key: str, config: APIConfig = APIConfig()):
        self.api_key = api_key
        self.config = config
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.semaphore = asyncio.Semaphore(config.max_concurrent_requests)
        self._request_times = []
    
    async def generate_response(self, prompt: str, max_tokens: int = 1000) -> str:
        """非同期でClaude APIを呼び出し応答を生成"""
        async with self.semaphore:
            await self._rate_limit()
            
            for attempt in range(self.config.retry_attempts):
                try:
                    logger.info(f"API呼び出し開始 (試行 {attempt + 1}/{self.config.retry_attempts})")
                    
                    response = await self.client.messages.create(
                        model="claude-3-haiku-20240307",
                        max_tokens=max_tokens,
                        messages=[{"role": "user", "content": prompt}]
                    )
                    
                    logger.info("API呼び出し成功")
                    return response.content[0].text
                    
                except Exception as e:
                    logger.warning(f"API呼び出し失敗 (試行 {attempt + 1}): {str(e)}")
                    
                    if attempt < self.config.retry_attempts - 1:
                        await asyncio.sleep(self.config.retry_delay * (2 ** attempt))  # exponential backoff
                    else:
                        return f"API呼び出しエラー: {str(e)}"
    
    async def _rate_limit(self):
        """レート制限の実装"""
        now = time.time()
        # 過去1分のリクエストをフィルタ
        self._request_times = [t for t in self._request_times if now - t < 60]
        
        if len(self._request_times) >= self.config.rate_limit_per_minute:
            sleep_time = 60 - (now - self._request_times[0])
            if sleep_time > 0:
                logger.info(f"レート制限により{sleep_time:.2f}秒待機")
                await asyncio.sleep(sleep_time)
        
        self._request_times.append(now)
    
    async def close(self):
        """クライアントの適切な終了処理"""
        await self.client.aclose()


# グローバル非同期Claudeクライアント
async_claude = AsyncClaudeClient(CLAUDE_API_KEY)


# =============================================================================
# 1. 非同期テンソル積（⊗）- 真の並行処理
# =============================================================================

class AsyncTensorProduct:
    """
    非同期テンソル積実装
    asyncioによる効率的な並行LLM呼び出し
    """
    
    def __init__(self, perspectives: List[str], integration_strategy: str = "synthesis"):
        self.perspectives = perspectives
        self.integration_strategy = integration_strategy
    
    async def apply(self, input_text: str) -> Dict[str, Any]:
        """非同期でテンソル積を実行"""
        logger.info(f"🔥 非同期テンソル積実行開始: {len(self.perspectives)}個の観点")
        
        start_time = time.time()
        
        # 真の非同期並行処理でLLM呼び出し
        individual_results = await self._async_parallel_calls(input_text)
        
        # 非同期統合処理
        integrated_result = await self._async_integration(input_text, individual_results)
        
        end_time = time.time()
        
        return {
            "input": input_text,
            "perspectives": self.perspectives,
            "individual_results": individual_results,
            "integrated_result": integrated_result,
            "processing_time": end_time - start_time,
            "async_processing": True
        }
    
    async def _async_parallel_calls(self, input_text: str) -> Dict[str, str]:
        """真の非同期並行でLLM呼び出し"""
        logger.info("非同期並行LLM呼び出し開始")
        
        # 各観点のタスクを作成
        tasks = []
        for perspective in self.perspectives:
            prompt = f"""
{perspective}の専門的観点から、以下について詳細に分析してください：

分析対象: {input_text}

{perspective}の立場から見た：
1. 主要な要素や特徴
2. 重要な課題や機会  
3. 具体的な影響や意義
4. 実践的な提案や対策

分析結果:
"""
            task = self._analyze_perspective(perspective, prompt)
            tasks.append(task)
        
        # 全タスクを並行実行
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 結果を辞書形式に変換
        individual_results = {}
        for i, result in enumerate(results):
            perspective = self.perspectives[i]
            if isinstance(result, Exception):
                individual_results[perspective] = f"エラー: {str(result)}"
                logger.error(f"❌ {perspective}観点でエラー: {result}")
            else:
                individual_results[perspective] = result
                logger.info(f"✅ {perspective}観点の分析完了")
        
        return individual_results
    
    async def _analyze_perspective(self, perspective: str, prompt: str) -> str:
        """単一観点の分析を非同期実行"""
        try:
            result = await async_claude.generate_response(prompt)
            return result
        except Exception as e:
            logger.error(f"観点{perspective}の分析でエラー: {e}")
            raise
    
    async def _async_integration(self, input_text: str, individual_results: Dict[str, str]) -> str:
        """非同期統合処理"""
        logger.info("🔄 非同期統合処理開始")
        
        integration_prompt = f"""
以下は「{input_text}」について異なる観点から行った分析結果です。
これらを統合して、包括的で洞察に富んだ統合見解を提示してください。

"""
        
        for perspective, result in individual_results.items():
            integration_prompt += f"""
【{perspective}の観点からの分析】
{result}

"""
        
        integration_prompt += f"""
統合タスク:
1. 各観点の重要な洞察を抽出
2. 観点間の相互関係や相乗効果を特定
3. 矛盾や対立点があれば調整・統合
4. より高次の理解や新たな視点を創出
5. 実践的で包括的な結論を提示

統合された包括的見解:
"""
        
        integrated_result = await async_claude.generate_response(integration_prompt, max_tokens=1500)
        logger.info("✅ 非同期統合処理完了")
        
        return integrated_result


# =============================================================================
# 2. 非同期自然変換 - 効率的な構造保存変換
# =============================================================================

class AsyncNaturalTransformation:
    """
    非同期自然変換実装
    効率的な構造保存変換
    """
    
    def __init__(self, source_domain: str, target_domain: str, transformation_rule: str):
        self.source_domain = source_domain
        self.target_domain = target_domain
        self.transformation_rule = transformation_rule
    
    async def apply_transformation(self, source_content: str) -> Dict[str, Any]:
        """非同期で自然変換実行"""
        logger.info(f"🔄 非同期自然変換実行: {self.source_domain} → {self.target_domain}")
        
        transformation_prompt = f"""
以下の{self.source_domain}の内容を{self.target_domain}に自然変換してください。

変換ルール: {self.transformation_rule}

元の内容（{self.source_domain}）:
{source_content}

変換要件:
1. 元の構造と論理的関係を保持
2. {self.target_domain}の特徴に適応
3. 情報の本質的価値を維持
4. 対象読者に適した表現に調整

変換結果（{self.target_domain}）:
"""
        
        start_time = time.time()
        transformed_result = await async_claude.generate_response(transformation_prompt, max_tokens=1200)
        end_time = time.time()
        
        return {
            "source_domain": self.source_domain,
            "target_domain": self.target_domain,
            "source_content": source_content,
            "transformed_content": transformed_result,
            "transformation_rule": self.transformation_rule,
            "processing_time": end_time - start_time
        }


# =============================================================================
# 3. 非同期アジョイント関手 - 効率的な双対性活用
# =============================================================================

class AsyncAdjointPair:
    """
    非同期アジョイント関手実装
    効率的な双対性活用
    """
    
    def __init__(self):
        self.name = "Async Free-Forgetful Adjunction"
    
    async def free_construction(self, constrained_input: str) -> Dict[str, Any]:
        """非同期で左随伴（自由化）を実行"""
        logger.info("🆓 非同期自由化変換実行中")
        
        free_prompt = f"""
以下の制約的な内容について、創造的自由度を最大化してください：

制約的入力: {constrained_input}

自由化の方向性:
1. 既存の制約や枠組みを取り払う
2. 創造的で革新的な可能性を探求
3. 多角的で柔軟な視点を導入
4. 未来志向的で実験的なアプローチ
5. 感情や直感も含めた全人的な発想

制約から解放された創造的な見解:
"""
        
        start_time = time.time()
        free_result = await async_claude.generate_response(free_prompt, max_tokens=1200)
        end_time = time.time()
        
        return {
            "type": "free_construction",
            "input": constrained_input,
            "result": free_result,
            "processing_time": end_time - start_time
        }
    
    async def forgetful_extraction(self, free_input: str) -> Dict[str, Any]:
        """非同期で右随伴（忘却/本質抽出）を実行"""
        logger.info("📝 非同期本質抽出実行中")
        
        forgetful_prompt = f"""
以下の自由で創造的な内容から、核心的で実践的な要素を抽出してください：

自由な入力: {free_input}

抽出の観点:
1. 実現可能な具体的要素の特定
2. 重要な制約や条件の明確化
3. 測定可能な成果や指標の設定
4. 実践的な行動計画の要素
5. 本質的価値の凝縮

抽出された本質的要素:
"""
        
        start_time = time.time()
        forgetful_result = await async_claude.generate_response(forgetful_prompt, max_tokens=1200)
        end_time = time.time()
        
        return {
            "type": "forgetful_extraction",
            "input": free_input,
            "result": forgetful_result,
            "processing_time": end_time - start_time
        }
    
    async def adjoint_cycle(self, initial_input: str) -> Dict[str, Any]:
        """非同期で随伴サイクルを実行"""
        logger.info("🔄 非同期随伴サイクル実行開始")
        
        # 制約 → 自由 と 自由 → 本質を並行実行することも可能
        # ただし、依存関係があるため逐次実行
        free_result = await self.free_construction(initial_input)
        forgetful_result = await self.forgetful_extraction(free_result["result"])
        
        return {
            "initial_input": initial_input,
            "free_construction": free_result,
            "forgetful_extraction": forgetful_result,
            "cycle_complete": True
        }


# =============================================================================
# 4. 非同期モナド - 効率的な文脈保持計算
# =============================================================================

class AsyncContextMonad:
    """
    非同期文脈保持モナド
    効率的な文脈管理と発展
    """
    
    def __init__(self, initial_context: str):
        self.current_context = initial_context
        self.history = []
        self.metadata = {}
    
    async def bind(self, new_input: str, context_type: str = "development") -> Dict[str, Any]:
        """非同期でモナドのbind演算を実行"""
        logger.info(f"🧠 非同期文脈保持発展実行: {context_type}")
        
        # 履歴に現在の文脈を追加
        self.history.append({
            "context": self.current_context,
            "timestamp": time.time()
        })
        
        development_prompt = f"""
文脈を考慮した知的発展を行ってください：

これまでの文脈履歴:
{self._format_history()}

現在の文脈: {self.current_context}

新しい入力: {new_input}

発展の要求:
1. 過去の文脈との整合性を保つ
2. 新しい入力を既存文脈に統合
3. より深い理解や洞察を生成
4. 自然で一貫した発展を実現
5. 次の文脈への橋渡しを準備

文脈を考慮した発展結果:
"""
        
        start_time = time.time()
        evolved_result = await async_claude.generate_response(development_prompt, max_tokens=1200)
        end_time = time.time()
        
        # 文脈を更新
        self.current_context = evolved_result
        
        return {
            "previous_context": self.history[-1]["context"] if self.history else "",
            "new_input": new_input,
            "evolved_context": evolved_result,
            "history_length": len(self.history),
            "processing_time": end_time - start_time
        }
    
    def _format_history(self) -> str:
        """履歴をフォーマット"""
        if not self.history:
            return "（履歴なし）"
        
        formatted = ""
        for i, entry in enumerate(self.history[-3:], 1):  # 最新3件
            formatted += f"{i}. {entry['context'][:100]}...\n"
        return formatted


# =============================================================================
# 実演・検証関数
# =============================================================================

async def demonstrate_async_tensor_product():
    """非同期テンソル積の実演"""
    print("=" * 80)
    print("🔥 非同期テンソル積実演 - asyncioによる真の並行処理")
    print("=" * 80)
    
    input_topic = "人工知能の教育分野での活用"
    perspectives = ["教育学", "技術", "倫理", "経済"]
    
    tensor = AsyncTensorProduct(perspectives, "synthesis")
    result = await tensor.apply(input_topic)
    
    print(f"\n📊 実行結果:")
    print(f"処理時間: {result['processing_time']:.2f}秒")
    print(f"非同期処理: {result['async_processing']}")
    
    print(f"\n🔍 個別分析結果:")
    for perspective, analysis in result['individual_results'].items():
        print(f"\n【{perspective}の観点】")
        print(analysis[:200] + "..." if len(analysis) > 200 else analysis)
    
    print(f"\n🎯 統合結果:")
    print(result['integrated_result'][:500] + "..." if len(result['integrated_result']) > 500 else result['integrated_result'])
    
    return result


async def demonstrate_async_natural_transformation():
    """非同期自然変換の実演"""
    print("\n" + "=" * 80)
    print("🔄 非同期自然変換実演 - 効率的な構造保存変換")
    print("=" * 80)
    
    technical_content = """
機械学習のアルゴリズムは、データから自動的にパターンを学習し予測を行う手法である。
主要なアプローチには教師あり学習、教師なし学習、強化学習があり、
それぞれ異なる問題設定と解法を提供する。深層学習は特に画像認識や
自然言語処理において顕著な性能向上を示している。
"""
    
    transformer = AsyncNaturalTransformation(
        "技術文書", "初心者向け教材",
        "専門用語を平易に、概念を具体例で、段階的理解を促進"
    )
    
    result = await transformer.apply_transformation(technical_content)
    
    print(f"変換時間: {result['processing_time']:.2f}秒")
    print(f"\n元の内容（技術文書）:")
    print(technical_content)
    
    print(f"\n変換結果（初心者向け教材）:")
    print(result['transformed_content'])
    
    return result


async def demonstrate_async_adjoint():
    """非同期アジョイント関手の実演"""
    print("\n" + "=" * 80)
    print("🔄 非同期アジョイント関手実演 - 効率的な双対性活用")
    print("=" * 80)
    
    constrained_problem = "企業の環境対策は法規制の枠内で最小限のコストで実施する"
    
    adjoint = AsyncAdjointPair()
    cycle_result = await adjoint.adjoint_cycle(constrained_problem)
    
    print(f"元の制約的問題:")
    print(constrained_problem)
    
    print(f"\n🆓 自由化結果:")
    print(cycle_result['free_construction']['result'][:300] + "...")
    
    print(f"\n📝 本質抽出結果:")
    print(cycle_result['forgetful_extraction']['result'][:300] + "...")
    
    return cycle_result


async def demonstrate_async_monad():
    """非同期モナドの実演"""
    print("\n" + "=" * 80)
    print("🧠 非同期モナド実演 - 効率的な文脈保持計算")
    print("=" * 80)
    
    # 初期文脈
    initial = "リモートワークの導入について検討を開始する"
    monad = AsyncContextMonad(initial)
    
    print(f"初期文脈: {initial}")
    
    # 並行発展（依存関係がないなら並行実行も可能）
    # この例では逐次実行
    result1 = await monad.bind("従業員の生産性への影響を調査したい", "analysis")
    print(f"\n第1発展: {result1['evolved_context'][:200]}...")
    
    result2 = await monad.bind("具体的な実装計画を作成する必要がある", "planning")
    print(f"\n第2発展: {result2['evolved_context'][:200]}...")
    
    return [result1, result2]


async def main():
    """非同期圏論的プロンプトエンジニアリング実演"""
    print("🚀 非同期圏論的プロンプトエンジニアリング実演開始")
    print("asyncioによる真の並行処理最適化")
    
    try:
        # 1. 非同期テンソル積
        tensor_result = await demonstrate_async_tensor_product()
        
        # 2. 非同期自然変換
        transform_result = await demonstrate_async_natural_transformation()
        
        # 3. 非同期アジョイント関手
        adjoint_result = await demonstrate_async_adjoint()
        
        # 4. 非同期モナド
        monad_results = await demonstrate_async_monad()
        
        print("\n" + "=" * 80)
        print("🎉 非同期圏論的プロンプトエンジニアリング実演完了!")
        print("=" * 80)
        print("✅ 全ての圏論的概念が非同期で最適化されました")
        print("⚡ 真の並行処理によるパフォーマンス向上を実現!")
        
    except Exception as e:
        logger.error(f"❌ エラーが発生しました: {e}")
        print("APIキーの確認やネットワーク接続を確認してください")
    
    finally:
        # クリーンアップ
        await async_claude.close()


if __name__ == "__main__":
    asyncio.run(main())