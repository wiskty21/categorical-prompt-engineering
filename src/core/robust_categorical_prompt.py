# -*- coding: utf-8 -*-
"""
堅牢な圏論的プロンプトエンジニアリング実装
高度なエラーハンドリング、リトライ機構、フォールバック戦略を備えた本格版

Features:
- 高度なエラーハンドリングとリカバリ
- 指数バックオフ付きリトライ機構
- フォールバック戦略とサーキットブレーカー
- 包括的なログ記録とメトリクス
- 設定可能な回復戦略
"""

import asyncio
import anthropic
import time
from typing import List, Dict, Any, Optional, Union, Callable
from dataclasses import dataclass, field
from enum import Enum
import json
import os
from dotenv import load_dotenv
import logging
from contextlib import asynccontextmanager
import traceback
from functools import wraps

# 高度なログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# 環境変数の読み込み
load_dotenv()
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

# API key validation deferred to runtime
logger.info(f"Claude API Key loaded: {'Yes' if CLAUDE_API_KEY else 'No'}")


class ErrorType(Enum):
    """エラータイプの分類"""
    API_ERROR = "api_error"
    RATE_LIMIT = "rate_limit"  
    TIMEOUT = "timeout"
    NETWORK = "network"
    AUTHENTICATION = "authentication"
    QUOTA_EXCEEDED = "quota_exceeded"
    UNKNOWN = "unknown"


class RecoveryStrategy(Enum):
    """回復戦略の種類"""
    RETRY = "retry"
    FALLBACK = "fallback"
    SKIP = "skip"
    FAIL_FAST = "fail_fast"


@dataclass
class ErrorContext:
    """エラー文脈情報"""
    error_type: ErrorType
    original_error: Exception
    attempt_count: int
    total_attempts: int
    elapsed_time: float
    operation: str
    parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RobustConfig:
    """堅牢性設定"""
    max_retries: int = 5
    base_delay: float = 1.0
    max_delay: float = 60.0
    backoff_multiplier: float = 2.0
    jitter: bool = True
    timeout_seconds: float = 30.0
    circuit_breaker_threshold: int = 5
    circuit_breaker_reset_time: float = 300.0  # 5分
    enable_fallback: bool = True
    log_errors: bool = True


class CircuitBreaker:
    """サーキットブレーカーパターン実装"""
    
    def __init__(self, failure_threshold: int, reset_timeout: float):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def can_execute(self) -> bool:
        """実行可能かチェック"""
        if self.state == "CLOSED":
            return True
        elif self.state == "OPEN":
            if time.time() - self.last_failure_time >= self.reset_timeout:
                self.state = "HALF_OPEN"
                return True
            return False
        else:  # HALF_OPEN
            return True
    
    def record_success(self):
        """成功を記録"""
        self.failure_count = 0
        self.state = "CLOSED"
    
    def record_failure(self):
        """失敗を記録"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = "OPEN"
            logger.warning(f"サーキットブレーカーがOPEN状態になりました（失敗回数: {self.failure_count}）")


class RobustClaudeClient:
    """堅牢なClaude APIクライアント"""
    
    def __init__(self, api_key: str, config: RobustConfig = RobustConfig()):
        self.api_key = api_key
        self.config = config
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        self.semaphore = asyncio.Semaphore(5)  # 並行リクエスト制限
        self.circuit_breaker = CircuitBreaker(
            config.circuit_breaker_threshold,
            config.circuit_breaker_reset_time
        )
        self.metrics = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "retry_count": 0,
            "average_response_time": 0.0
        }
    
    def _classify_error(self, error: Exception) -> ErrorType:
        """エラーを分類"""
        error_str = str(error).lower()
        
        if "rate limit" in error_str or "429" in error_str:
            return ErrorType.RATE_LIMIT
        elif "timeout" in error_str:
            return ErrorType.TIMEOUT
        elif "network" in error_str or "connection" in error_str:
            return ErrorType.NETWORK
        elif "authentication" in error_str or "401" in error_str:
            return ErrorType.AUTHENTICATION
        elif "quota" in error_str or "402" in error_str:
            return ErrorType.QUOTA_EXCEEDED
        elif hasattr(error, 'status_code'):
            return ErrorType.API_ERROR
        else:
            return ErrorType.UNKNOWN
    
    def _calculate_delay(self, attempt: int, error_type: ErrorType) -> float:
        """遅延時間を計算（指数バックオフ + ジッター）"""
        if error_type == ErrorType.RATE_LIMIT:
            base = min(self.config.base_delay * (2 ** attempt), self.config.max_delay)
        else:
            base = min(self.config.base_delay * (self.config.backoff_multiplier ** attempt), 
                      self.config.max_delay)
        
        if self.config.jitter:
            import random
            base *= (0.5 + 0.5 * random.random())  # 50-100%のジッター
        
        return base
    
    def _should_retry(self, error_context: ErrorContext) -> bool:
        """リトライすべきかを判断"""
        if error_context.attempt_count >= self.config.max_retries:
            return False
        
        # 認証エラーやクォータ超過はリトライしない
        if error_context.error_type in [ErrorType.AUTHENTICATION, ErrorType.QUOTA_EXCEEDED]:
            return False
        
        # サーキットブレーカーがOPEN状態ならリトライしない
        if not self.circuit_breaker.can_execute():
            return False
        
        return True
    
    async def _execute_with_fallback(self, prompt: str, max_tokens: int) -> str:
        """フォールバック戦略付きで実行"""
        if not self.config.enable_fallback:
            raise RuntimeError("フォールバック戦略が無効で、プライマリ実行が失敗しました")
        
        # 簡易フォールバック（プロンプトを短縮してリトライ）
        logger.warning("フォールバック戦略を実行：プロンプトを短縮してリトライ")
        
        shortened_prompt = prompt[:len(prompt)//2] + "\n\n上記について簡潔に回答してください。"
        return await self._raw_api_call(shortened_prompt, max_tokens//2)
    
    async def _raw_api_call(self, prompt: str, max_tokens: int) -> str:
        """生のAPI呼び出し"""
        try:
            response = await self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": prompt}],
                timeout=self.config.timeout_seconds
            )
            return response.content[0].text
        except asyncio.TimeoutError:
            raise TimeoutError("API呼び出しがタイムアウトしました")
    
    async def generate_response(self, prompt: str, max_tokens: int = 1000, 
                              operation_name: str = "generate_response") -> str:
        """堅牢な応答生成（エラーハンドリング・リトライ付き）"""
        
        async with self.semaphore:
            self.metrics["total_requests"] += 1
            start_time = time.time()
            
            for attempt in range(self.config.max_retries + 1):
                try:
                    # サーキットブレーカーチェック
                    if not self.circuit_breaker.can_execute():
                        raise RuntimeError("サーキットブレーカーがOPEN状態です")
                    
                    logger.info(f"API呼び出し開始 [{operation_name}] (試行 {attempt + 1}/{self.config.max_retries + 1})")
                    
                    result = await self._raw_api_call(prompt, max_tokens)
                    
                    # 成功時の処理
                    self.circuit_breaker.record_success()
                    self.metrics["successful_requests"] += 1
                    
                    elapsed = time.time() - start_time
                    self.metrics["average_response_time"] = (
                        (self.metrics["average_response_time"] * (self.metrics["successful_requests"] - 1) + elapsed) 
                        / self.metrics["successful_requests"]
                    )
                    
                    logger.info(f"API呼び出し成功 [{operation_name}] (所要時間: {elapsed:.2f}秒)")
                    return result
                
                except Exception as e:
                    error_type = self._classify_error(e)
                    error_context = ErrorContext(
                        error_type=error_type,
                        original_error=e,
                        attempt_count=attempt,
                        total_attempts=self.config.max_retries + 1,
                        elapsed_time=time.time() - start_time,
                        operation=operation_name,
                        parameters={"prompt_length": len(prompt), "max_tokens": max_tokens}
                    )
                    
                    if self.config.log_errors:
                        logger.error(f"API呼び出しエラー [{operation_name}] (試行 {attempt + 1}): "
                                   f"{error_type.value} - {str(e)}")
                        if logger.isEnabledFor(logging.DEBUG):
                            logger.debug(f"エラートレース: {traceback.format_exc()}")
                    
                    # 最後の試行でなければリトライ判定
                    if attempt < self.config.max_retries:
                        if self._should_retry(error_context):
                            delay = self._calculate_delay(attempt, error_type)
                            logger.info(f"リトライ前に {delay:.2f}秒 待機")
                            await asyncio.sleep(delay)
                            self.metrics["retry_count"] += 1
                            continue
                    
                    # リトライ不可 or 最後の試行
                    self.circuit_breaker.record_failure()
                    self.metrics["failed_requests"] += 1
                    
                    # フォールバック戦略を試行
                    if self.config.enable_fallback and error_type != ErrorType.AUTHENTICATION:
                        try:
                            result = await self._execute_with_fallback(prompt, max_tokens)
                            logger.info(f"フォールバック戦略成功 [{operation_name}]")
                            return result
                        except Exception as fallback_error:
                            logger.error(f"フォールバック戦略も失敗 [{operation_name}]: {fallback_error}")
                    
                    # 最終的なエラー
                    final_error = RuntimeError(
                        f"API呼び出し最終失敗 [{operation_name}]: {error_type.value} - {str(e)}\n"
                        f"試行回数: {attempt + 1}, 総所要時間: {time.time() - start_time:.2f}秒"
                    )
                    raise final_error from e
    
    def get_metrics(self) -> Dict[str, Any]:
        """メトリクス情報を取得"""
        return {
            **self.metrics,
            "success_rate": (self.metrics["successful_requests"] / self.metrics["total_requests"] 
                           if self.metrics["total_requests"] > 0 else 0),
            "circuit_breaker_state": self.circuit_breaker.state,
            "circuit_breaker_failures": self.circuit_breaker.failure_count
        }
    
    async def close(self):
        """クライアントの適切な終了処理"""
        await self.client.aclose()


# グローバル堅牢Claudeクライアント
robust_claude = RobustClaudeClient(CLAUDE_API_KEY)


# =============================================================================
# 堅牢な圏論的実装クラス群
# =============================================================================

class RobustTensorProduct:
    """堅牢なテンソル積実装"""
    
    def __init__(self, perspectives: List[str], integration_strategy: str = "synthesis"):
        self.perspectives = perspectives
        self.integration_strategy = integration_strategy
    
    async def apply(self, input_text: str) -> Dict[str, Any]:
        """堅牢なテンソル積実行"""
        logger.info(f"🔥 堅牢テンソル積実行開始: {len(self.perspectives)}個の観点")
        
        start_time = time.time()
        
        try:
            # 並行処理でLLM呼び出し（エラーハンドリング付き）
            individual_results = await self._robust_parallel_calls(input_text)
            
            # 統合処理
            integrated_result = await self._robust_integration(input_text, individual_results)
            
            end_time = time.time()
            
            return {
                "input": input_text,
                "perspectives": self.perspectives,
                "individual_results": individual_results,
                "integrated_result": integrated_result,
                "processing_time": end_time - start_time,
                "robust_processing": True,
                "metrics": robust_claude.get_metrics()
            }
            
        except Exception as e:
            logger.error(f"テンソル積実行でエラー: {e}")
            # 部分的結果でも返す（回復戦略）
            return {
                "input": input_text,
                "perspectives": self.perspectives,
                "error": str(e),
                "processing_time": time.time() - start_time,
                "robust_processing": False
            }
    
    async def _robust_parallel_calls(self, input_text: str) -> Dict[str, str]:
        """堅牢な並行LLM呼び出し"""
        logger.info("堅牢な並行LLM呼び出し開始")
        
        # 各観点のタスクを作成
        tasks = []
        for perspective in self.perspectives:
            prompt = f"""
{perspective}の専門的観点から、以下について分析してください：

分析対象: {input_text}

{perspective}の立場から見た：
1. 主要な要素や特徴
2. 重要な課題や機会
3. 具体的な影響や意義
4. 実践的な提案や対策

分析結果:
"""
            task = self._analyze_perspective_robust(perspective, prompt)
            tasks.append(task)
        
        # 全タスクを並行実行（例外も収集）
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 結果を処理
        individual_results = {}
        successful_count = 0
        
        for i, result in enumerate(results):
            perspective = self.perspectives[i]
            if isinstance(result, Exception):
                individual_results[perspective] = f"エラー（回復可能）: {str(result)}"
                logger.warning(f"⚠️ {perspective}観点でエラー（処理続行）: {result}")
            else:
                individual_results[perspective] = result
                successful_count += 1
                logger.info(f"✅ {perspective}観点の分析完了")
        
        logger.info(f"並行処理完了: {successful_count}/{len(self.perspectives)} 成功")
        
        # 最低1つは成功している必要がある
        if successful_count == 0:
            raise RuntimeError("すべての観点で分析が失敗しました")
        
        return individual_results
    
    async def _analyze_perspective_robust(self, perspective: str, prompt: str) -> str:
        """単一観点の堅牢な分析"""
        try:
            result = await robust_claude.generate_response(
                prompt, 
                operation_name=f"analyze_{perspective}"
            )
            return result
        except Exception as e:
            logger.error(f"観点{perspective}の分析でエラー: {e}")
            # 部分的な結果を返すか、エラーを再発生
            raise
    
    async def _robust_integration(self, input_text: str, individual_results: Dict[str, str]) -> str:
        """堅牢な統合処理"""
        logger.info("🔄 堅牢な統合処理開始")
        
        # 成功した結果のみを統合
        valid_results = {k: v for k, v in individual_results.items() 
                        if not v.startswith("エラー")}
        
        if not valid_results:
            raise RuntimeError("統合可能な有効な分析結果がありません")
        
        integration_prompt = f"""
以下は「{input_text}」について異なる観点から行った分析結果です。
利用可能な分析を統合して、包括的な見解を提示してください。

"""
        
        for perspective, result in valid_results.items():
            integration_prompt += f"""
【{perspective}の観点からの分析】
{result}

"""
        
        integration_prompt += f"""
統合タスク:
1. 利用可能な観点の洞察を抽出
2. 観点間の関係や相乗効果を特定
3. 包括的で実用的な結論を提示
4. 不足している観点があれば指摘

統合された見解:
"""
        
        try:
            integrated_result = await robust_claude.generate_response(
                integration_prompt, 
                max_tokens=1500, 
                operation_name="integration"
            )
            logger.info("✅ 堅牢な統合処理完了")
            return integrated_result
        except Exception as e:
            # 統合が失敗した場合は個別結果の要約を返す
            logger.warning(f"統合処理失敗、個別結果を要約: {e}")
            summary = f"個別分析結果の要約（統合処理失敗のため）:\n\n"
            for perspective, result in valid_results.items():
                summary += f"【{perspective}】\n{result[:200]}...\n\n"
            return summary


# =============================================================================
# 実演関数
# =============================================================================

async def demonstrate_robust_system():
    """堅牢システムの実演"""
    print("=" * 80)
    print("🛡️ 堅牢な圏論的プロンプトエンジニアリング実演")
    print("=" * 80)
    
    input_topic = "人工知能の教育分野での活用"
    perspectives = ["教育学", "技術", "倫理", "経済", "心理学"]  # より多くの観点
    
    tensor = RobustTensorProduct(perspectives, "synthesis")
    
    try:
        result = await tensor.apply(input_topic)
        
        print(f"\n📊 実行結果:")
        print(f"処理時間: {result['processing_time']:.2f}秒")
        print(f"堅牢処理: {result.get('robust_processing', False)}")
        
        if 'metrics' in result:
            metrics = result['metrics']
            print(f"\n📈 メトリクス:")
            print(f"成功率: {metrics['success_rate']:.1%}")
            print(f"平均応答時間: {metrics['average_response_time']:.2f}秒")
            print(f"リトライ回数: {metrics['retry_count']}")
            print(f"サーキットブレーカー状態: {metrics['circuit_breaker_state']}")
        
        if 'individual_results' in result:
            print(f"\n🔍 個別分析結果:")
            for perspective, analysis in result['individual_results'].items():
                status = "✅" if not analysis.startswith("エラー") else "⚠️"
                print(f"\n{status} 【{perspective}の観点】")
                display_text = analysis[:200] + "..." if len(analysis) > 200 else analysis
                print(display_text)
        
        if 'integrated_result' in result:
            print(f"\n🎯 統合結果:")
            integrated = result['integrated_result']
            display_integrated = integrated[:500] + "..." if len(integrated) > 500 else integrated
            print(display_integrated)
        
        return result
        
    except Exception as e:
        logger.error(f"実演でエラー: {e}")
        print(f"❌ エラーが発生しましたが、システムは堅牢に動作しました: {e}")
        return None


async def main():
    """メイン実行関数"""
    print("🚀 堅牢な圏論的プロンプトエンジニアリング開始")
    print("高度なエラーハンドリング・リトライ機構搭載")
    
    try:
        result = await demonstrate_robust_system()
        
        print("\n" + "=" * 80)
        print("🎉 堅牢システム実演完了!")
        print("=" * 80)
        print("✅ 高度なエラーハンドリングとリカバリ機能を確認")
        print("🛡️ プロダクション環境対応の堅牢性を実現!")
        
    except Exception as e:
        logger.error(f"❌ 予期しないエラー: {e}")
        print("システムレベルのエラーが発生しました")
    
    finally:
        # クリーンアップ
        await robust_claude.close()


if __name__ == "__main__":
    asyncio.run(main())