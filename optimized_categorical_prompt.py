# -*- coding: utf-8 -*-
"""
最適化された圏論的プロンプトエンジニアリング実装
バッチ処理・キャッシュ機能・パフォーマンス最適化を搭載した完全版

Features:
- インテリジェントキャッシュシステム
- バッチ処理によるAPI効率化
- アダプティブレート制御
- メモリ効率的な処理
- パフォーマンス監視とメトリクス
- 動的リソース管理
"""

import asyncio
import anthropic
import time
import hashlib
import pickle
from typing import List, Dict, Any, Optional, Union, Tuple
from dataclasses import dataclass, field
from collections import OrderedDict, defaultdict
import json
import os
from dotenv import load_dotenv
import logging
from contextlib import asynccontextmanager
import threading
from concurrent.futures import ThreadPoolExecutor
import gc
import psutil
import weakref

# 最適化されたログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# 環境変数の読み込み
load_dotenv()
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

if not CLAUDE_API_KEY:
    raise ValueError("CLAUDE_API_KEY が設定されていません。.envファイルを確認してください。")


@dataclass
class CacheConfig:
    """キャッシュ設定"""
    max_size: int = 1000
    ttl_seconds: float = 3600.0  # 1時間
    enable_persistence: bool = False
    persistence_file: str = "cache.pkl"
    memory_limit_mb: int = 100


@dataclass
class BatchConfig:
    """バッチ処理設定"""
    max_batch_size: int = 10
    batch_timeout: float = 2.0
    enable_adaptive_batching: bool = True
    min_batch_size: int = 2


@dataclass
class OptimizationConfig:
    """最適化設定"""
    cache_config: CacheConfig = field(default_factory=CacheConfig)
    batch_config: BatchConfig = field(default_factory=BatchConfig)
    enable_memory_optimization: bool = True
    enable_performance_monitoring: bool = True
    max_concurrent_requests: int = 8
    adaptive_rate_control: bool = True


class LRUCache:
    """高性能LRUキャッシュ実装"""
    
    def __init__(self, max_size: int, ttl_seconds: float):
        self.max_size = max_size
        self.ttl_seconds = ttl_seconds
        self.cache = OrderedDict()
        self.timestamps = {}
        self.lock = threading.RLock()
        self.hit_count = 0
        self.miss_count = 0
    
    def _hash_key(self, key: Any) -> str:
        """キーのハッシュ化"""
        if isinstance(key, str):
            return hashlib.md5(key.encode()).hexdigest()
        else:
            return hashlib.md5(str(key).encode()).hexdigest()
    
    def _is_expired(self, key: str) -> bool:
        """期限切れチェック"""
        if key not in self.timestamps:
            return True
        return time.time() - self.timestamps[key] > self.ttl_seconds
    
    def get(self, key: Any) -> Optional[Any]:
        """キャッシュから取得"""
        with self.lock:
            hashed_key = self._hash_key(key)
            
            if hashed_key in self.cache and not self._is_expired(hashed_key):
                # LRU更新
                value = self.cache.pop(hashed_key)
                self.cache[hashed_key] = value
                self.hit_count += 1
                return value
            
            self.miss_count += 1
            return None
    
    def put(self, key: Any, value: Any) -> None:
        """キャッシュに保存"""
        with self.lock:
            hashed_key = self._hash_key(key)
            
            # 既存エントリの更新
            if hashed_key in self.cache:
                self.cache.pop(hashed_key)
            
            # 容量チェック
            while len(self.cache) >= self.max_size:
                oldest_key, _ = self.cache.popitem(last=False)
                self.timestamps.pop(oldest_key, None)
            
            # 新エントリ追加
            self.cache[hashed_key] = value
            self.timestamps[hashed_key] = time.time()
    
    def clear_expired(self) -> int:
        """期限切れエントリを削除"""
        with self.lock:
            expired_keys = []
            for key in self.cache:
                if self._is_expired(key):
                    expired_keys.append(key)
            
            for key in expired_keys:
                self.cache.pop(key, None)
                self.timestamps.pop(key, None)
            
            return len(expired_keys)
    
    def stats(self) -> Dict[str, Any]:
        """キャッシュ統計"""
        with self.lock:
            total_requests = self.hit_count + self.miss_count
            hit_rate = self.hit_count / total_requests if total_requests > 0 else 0
            
            return {
                "size": len(self.cache),
                "max_size": self.max_size,
                "hit_count": self.hit_count,
                "miss_count": self.miss_count,
                "hit_rate": hit_rate,
                "memory_usage_mb": self._estimate_memory_usage()
            }
    
    def _estimate_memory_usage(self) -> float:
        """メモリ使用量推定"""
        try:
            return len(pickle.dumps(self.cache)) / (1024 * 1024)
        except:
            return 0.0


class BatchProcessor:
    """インテリジェントバッチ処理"""
    
    def __init__(self, config: BatchConfig):
        self.config = config
        self.pending_requests = []
        self.batch_lock = asyncio.Lock()
        self.batch_event = asyncio.Event()
        self.processing = False
        self.metrics = {
            "total_batches": 0,
            "total_requests": 0,
            "average_batch_size": 0.0,
            "batch_efficiency": 0.0
        }
    
    async def add_request(self, request_data: Dict[str, Any]) -> Any:
        """リクエストをバッチに追加"""
        future = asyncio.get_event_loop().create_future()
        
        async with self.batch_lock:
            self.pending_requests.append({
                "data": request_data,
                "future": future,
                "timestamp": time.time()
            })
            
            # バッチサイズに達したか、アダプティブ条件を満たす場合
            if (len(self.pending_requests) >= self.config.max_batch_size or
                (self.config.enable_adaptive_batching and 
                 self._should_process_batch())):
                
                if not self.processing:
                    asyncio.create_task(self._process_batch())
        
        return await future
    
    def _should_process_batch(self) -> bool:
        """バッチ処理を開始すべきかの判定"""
        if len(self.pending_requests) < self.config.min_batch_size:
            return False
        
        # 最古のリクエストがタイムアウトしそうな場合
        if self.pending_requests:
            oldest_time = self.pending_requests[0]["timestamp"]
            if time.time() - oldest_time >= self.config.batch_timeout:
                return True
        
        return False
    
    async def _process_batch(self):
        """バッチを処理"""
        async with self.batch_lock:
            if self.processing or not self.pending_requests:
                return
            
            self.processing = True
            batch = self.pending_requests.copy()
            self.pending_requests.clear()
        
        try:
            logger.info(f"バッチ処理開始: {len(batch)}件のリクエスト")
            
            # 実際のバッチ処理（並行実行）
            tasks = []
            for item in batch:
                task = self._process_single_request(item["data"])
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 結果を各Futureに設定
            for i, result in enumerate(results):
                future = batch[i]["future"]
                if isinstance(result, Exception):
                    future.set_exception(result)
                else:
                    future.set_result(result)
            
            # メトリクス更新
            self.metrics["total_batches"] += 1
            self.metrics["total_requests"] += len(batch)
            self.metrics["average_batch_size"] = (
                self.metrics["total_requests"] / self.metrics["total_batches"]
            )
            
            logger.info(f"バッチ処理完了: {len(batch)}件")
            
        except Exception as e:
            logger.error(f"バッチ処理エラー: {e}")
            # エラーの場合は全Futureにエラーを設定
            for item in batch:
                if not item["future"].done():
                    item["future"].set_exception(e)
        
        finally:
            self.processing = False
    
    async def _process_single_request(self, request_data: Dict[str, Any]) -> Any:
        """単一リクエストの処理（サブクラスで実装）"""
        raise NotImplementedError()


class OptimizedClaudeClient:
    """最適化されたClaude APIクライアント"""
    
    def __init__(self, api_key: str, config: OptimizationConfig = OptimizationConfig()):
        self.api_key = api_key
        self.config = config
        self.client = anthropic.AsyncAnthropic(api_key=api_key)
        
        # キャッシュシステム
        self.cache = LRUCache(
            config.cache_config.max_size,
            config.cache_config.ttl_seconds
        )
        
        # バッチプロセッサ
        self.batch_processor = ClaudeBatchProcessor(
            config.batch_config,
            self.client
        )
        
        # 並行制御
        self.semaphore = asyncio.Semaphore(config.max_concurrent_requests)
        
        # パフォーマンス監視
        self.performance_monitor = PerformanceMonitor() if config.enable_performance_monitoring else None
        
        # メモリ管理
        self.memory_manager = MemoryManager() if config.enable_memory_optimization else None
        
        # アダプティブレート制御
        self.rate_controller = AdaptiveRateController() if config.adaptive_rate_control else None
    
    async def generate_response(self, prompt: str, max_tokens: int = 1000, 
                              use_cache: bool = True, use_batch: bool = False,
                              operation_name: str = "generate_response") -> str:
        """最適化された応答生成"""
        
        # キャッシュチェック
        if use_cache:
            cache_key = f"{prompt}:{max_tokens}"
            cached_result = self.cache.get(cache_key)
            if cached_result is not None:
                logger.debug(f"キャッシュヒット [{operation_name}]")
                return cached_result
        
        # バッチ処理
        if use_batch:
            request_data = {
                "prompt": prompt,
                "max_tokens": max_tokens,
                "operation_name": operation_name
            }
            result = await self.batch_processor.add_request(request_data)
        else:
            # 直接処理
            result = await self._direct_process(prompt, max_tokens, operation_name)
        
        # キャッシュに保存
        if use_cache and result:
            self.cache.put(cache_key, result)
        
        return result
    
    async def _direct_process(self, prompt: str, max_tokens: int, operation_name: str) -> str:
        """直接処理"""
        async with self.semaphore:
            # パフォーマンス監視開始
            if self.performance_monitor:
                self.performance_monitor.start_operation(operation_name)
            
            # レート制御
            if self.rate_controller:
                await self.rate_controller.wait_if_needed()
            
            try:
                response = await self.client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                result = response.content[0].text
                
                # レート制御更新
                if self.rate_controller:
                    self.rate_controller.record_success()
                
                return result
                
            except Exception as e:
                if self.rate_controller:
                    self.rate_controller.record_failure()
                raise
            
            finally:
                # パフォーマンス監視終了
                if self.performance_monitor:
                    self.performance_monitor.end_operation(operation_name)
                
                # メモリ管理
                if self.memory_manager:
                    self.memory_manager.check_and_optimize()
    
    def get_optimization_stats(self) -> Dict[str, Any]:
        """最適化統計を取得"""
        stats = {
            "cache_stats": self.cache.stats(),
            "batch_stats": self.batch_processor.metrics
        }
        
        if self.performance_monitor:
            stats["performance_stats"] = self.performance_monitor.get_stats()
        
        if self.rate_controller:
            stats["rate_control_stats"] = self.rate_controller.get_stats()
        
        if self.memory_manager:
            stats["memory_stats"] = self.memory_manager.get_stats()
        
        return stats
    
    async def cleanup(self):
        """リソース解放"""
        # 期限切れキャッシュエントリ削除
        expired_count = self.cache.clear_expired()
        logger.info(f"期限切れキャッシュエントリを{expired_count}件削除")
        
        # メモリ最適化
        if self.memory_manager:
            self.memory_manager.force_cleanup()
        
        # クライアント終了
        await self.client.aclose()


class ClaudeBatchProcessor(BatchProcessor):
    """Claude専用バッチプロセッサ"""
    
    def __init__(self, config: BatchConfig, client: anthropic.AsyncAnthropic):
        super().__init__(config)
        self.client = client
    
    async def _process_single_request(self, request_data: Dict[str, Any]) -> str:
        """Claude APIの単一リクエスト処理"""
        try:
            response = await self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=request_data["max_tokens"],
                messages=[{"role": "user", "content": request_data["prompt"]}]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"バッチ内リクエストエラー: {e}")
            raise


class PerformanceMonitor:
    """パフォーマンス監視"""
    
    def __init__(self):
        self.operations = defaultdict(list)
        self.active_operations = {}
    
    def start_operation(self, operation_name: str) -> str:
        """操作開始"""
        operation_id = f"{operation_name}_{time.time()}"
        self.active_operations[operation_id] = {
            "name": operation_name,
            "start_time": time.time(),
            "memory_before": self._get_memory_usage()
        }
        return operation_id
    
    def end_operation(self, operation_name: str) -> None:
        """操作終了"""
        # 最新の同名操作を終了
        for op_id, op_data in list(self.active_operations.items()):
            if op_data["name"] == operation_name:
                end_time = time.time()
                duration = end_time - op_data["start_time"]
                memory_after = self._get_memory_usage()
                
                self.operations[operation_name].append({
                    "duration": duration,
                    "memory_delta": memory_after - op_data["memory_before"],
                    "timestamp": end_time
                })
                
                del self.active_operations[op_id]
                break
    
    def _get_memory_usage(self) -> float:
        """メモリ使用量取得"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        except:
            return 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """統計取得"""
        stats = {}
        
        for op_name, op_data in self.operations.items():
            if op_data:
                durations = [op["duration"] for op in op_data]
                memory_deltas = [op["memory_delta"] for op in op_data]
                
                stats[op_name] = {
                    "count": len(op_data),
                    "avg_duration": sum(durations) / len(durations),
                    "max_duration": max(durations),
                    "min_duration": min(durations),
                    "avg_memory_delta": sum(memory_deltas) / len(memory_deltas),
                    "total_duration": sum(durations)
                }
        
        return stats


class MemoryManager:
    """メモリ管理"""
    
    def __init__(self, threshold_mb: float = 500.0):
        self.threshold_mb = threshold_mb
        self.last_cleanup = time.time()
        self.cleanup_interval = 300  # 5分
    
    def check_and_optimize(self) -> None:
        """メモリチェックと最適化"""
        current_memory = self._get_memory_usage()
        
        if (current_memory > self.threshold_mb or 
            time.time() - self.last_cleanup > self.cleanup_interval):
            self.force_cleanup()
    
    def force_cleanup(self) -> None:
        """強制クリーンアップ"""
        before_memory = self._get_memory_usage()
        
        # ガベージコレクション実行
        collected = gc.collect()
        
        after_memory = self._get_memory_usage()
        freed_mb = before_memory - after_memory
        
        logger.info(f"メモリクリーンアップ実行: {collected}オブジェクト削除, "
                   f"{freed_mb:.1f}MB解放")
        
        self.last_cleanup = time.time()
    
    def _get_memory_usage(self) -> float:
        """メモリ使用量取得"""
        try:
            process = psutil.Process()
            return process.memory_info().rss / 1024 / 1024  # MB
        except:
            return 0.0
    
    def get_stats(self) -> Dict[str, Any]:
        """メモリ統計"""
        try:
            process = psutil.Process()
            memory_info = process.memory_info()
            
            return {
                "rss_mb": memory_info.rss / 1024 / 1024,
                "vms_mb": memory_info.vms / 1024 / 1024,
                "threshold_mb": self.threshold_mb,
                "last_cleanup": self.last_cleanup
            }
        except:
            return {}


class AdaptiveRateController:
    """アダプティブレート制御"""
    
    def __init__(self):
        self.success_count = 0
        self.failure_count = 0
        self.current_delay = 0.0
        self.last_request_time = 0.0
        self.target_success_rate = 0.95
        self.adjustment_factor = 1.2
        self.min_delay = 0.0
        self.max_delay = 5.0
    
    async def wait_if_needed(self) -> None:
        """必要に応じて待機"""
        if self.current_delay > 0:
            await asyncio.sleep(self.current_delay)
        
        self.last_request_time = time.time()
    
    def record_success(self) -> None:
        """成功記録"""
        self.success_count += 1
        self._adjust_rate()
    
    def record_failure(self) -> None:
        """失敗記録"""
        self.failure_count += 1
        self._adjust_rate()
    
    def _adjust_rate(self) -> None:
        """レート調整"""
        total_requests = self.success_count + self.failure_count
        
        if total_requests > 10:  # 十分なサンプルがある場合
            current_success_rate = self.success_count / total_requests
            
            if current_success_rate < self.target_success_rate:
                # 成功率が低い場合は遅延を増加
                self.current_delay = min(
                    self.current_delay * self.adjustment_factor,
                    self.max_delay
                )
            else:
                # 成功率が高い場合は遅延を減少
                self.current_delay = max(
                    self.current_delay / self.adjustment_factor,
                    self.min_delay
                )
    
    def get_stats(self) -> Dict[str, Any]:
        """レート制御統計"""
        total_requests = self.success_count + self.failure_count
        success_rate = self.success_count / total_requests if total_requests > 0 else 0
        
        return {
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "success_rate": success_rate,
            "current_delay": self.current_delay,
            "target_success_rate": self.target_success_rate
        }


# =============================================================================
# 最適化された圏論的クラス群
# =============================================================================

class OptimizedTensorProduct:
    """最適化されたテンソル積"""
    
    def __init__(self, perspectives: List[str], integration_strategy: str = "synthesis",
                 client: OptimizedClaudeClient = None):
        self.perspectives = perspectives
        self.integration_strategy = integration_strategy
        self.client = client or OptimizedClaudeClient(CLAUDE_API_KEY)
    
    async def apply(self, input_text: str, use_cache: bool = True, 
                   use_batch: bool = True) -> Dict[str, Any]:
        """最適化されたテンソル積実行"""
        logger.info(f"🚀 最適化テンソル積実行: {len(self.perspectives)}観点 "
                   f"(キャッシュ:{use_cache}, バッチ:{use_batch})")
        
        start_time = time.time()
        
        # 並行分析
        individual_results = await self._optimized_parallel_analysis(
            input_text, use_cache, use_batch
        )
        
        # 最適化統合
        integrated_result = await self._optimized_integration(
            input_text, individual_results, use_cache
        )
        
        end_time = time.time()
        
        return {
            "input": input_text,
            "perspectives": self.perspectives,
            "individual_results": individual_results,
            "integrated_result": integrated_result,
            "processing_time": end_time - start_time,
            "optimization_stats": self.client.get_optimization_stats(),
            "optimized_processing": True
        }
    
    async def _optimized_parallel_analysis(self, input_text: str, 
                                         use_cache: bool, use_batch: bool) -> Dict[str, str]:
        """最適化された並行分析"""
        tasks = []
        
        for perspective in self.perspectives:
            prompt = f"""
{perspective}の観点から以下を分析:

対象: {input_text}

{perspective}として重要な点:
1. 核心要素
2. 主要課題
3. 実践的提案

分析結果:
"""
            
            task = self.client.generate_response(
                prompt,
                max_tokens=800,
                use_cache=use_cache,
                use_batch=use_batch,
                operation_name=f"analyze_{perspective}"
            )
            tasks.append((perspective, task))
        
        # 結果収集
        individual_results = {}
        for perspective, task in tasks:
            try:
                result = await task
                individual_results[perspective] = result
                logger.info(f"✅ {perspective}分析完了")
            except Exception as e:
                individual_results[perspective] = f"エラー: {str(e)}"
                logger.warning(f"⚠️ {perspective}分析でエラー: {e}")
        
        return individual_results
    
    async def _optimized_integration(self, input_text: str, 
                                   individual_results: Dict[str, str],
                                   use_cache: bool) -> str:
        """最適化された統合処理"""
        # 成功した結果のみ統合
        valid_results = {k: v for k, v in individual_results.items() 
                        if not v.startswith("エラー")}
        
        integration_prompt = f"""
「{input_text}」の多角的分析を統合:

"""
        
        for perspective, result in valid_results.items():
            integration_prompt += f"【{perspective}】{result[:300]}...\n\n"
        
        integration_prompt += "統合見解:"
        
        return await self.client.generate_response(
            integration_prompt,
            max_tokens=1200,
            use_cache=use_cache,
            use_batch=False,  # 統合は単独処理
            operation_name="integration"
        )


# =============================================================================
# 実演関数
# =============================================================================

async def demonstrate_optimization():
    """最適化機能の実演"""
    print("🚀 最適化された圏論的プロンプトエンジニアリング実演")
    print("=" * 80)
    
    # 設定
    config = OptimizationConfig(
        cache_config=CacheConfig(max_size=100, ttl_seconds=1800),
        batch_config=BatchConfig(max_batch_size=5, batch_timeout=1.0),
        enable_memory_optimization=True,
        enable_performance_monitoring=True,
        adaptive_rate_control=True
    )
    
    client = OptimizedClaudeClient(CLAUDE_API_KEY, config)
    
    input_topic = "持続可能な都市開発"
    perspectives = ["環境", "経済", "社会", "技術", "政策"]
    
    tensor = OptimizedTensorProduct(perspectives, client=client)
    
    try:
        # 初回実行（キャッシュなし）
        print("\n🔄 初回実行（キャッシュなし）")
        result1 = await tensor.apply(input_topic, use_cache=False, use_batch=True)
        
        print(f"処理時間: {result1['processing_time']:.2f}秒")
        
        # 2回目実行（キャッシュあり）
        print("\n🔄 2回目実行（キャッシュあり）")
        result2 = await tensor.apply(input_topic, use_cache=True, use_batch=True)
        
        print(f"処理時間: {result2['processing_time']:.2f}秒")
        print(f"高速化: {result1['processing_time']/result2['processing_time']:.1f}倍")
        
        # 最適化統計
        stats = client.get_optimization_stats()
        print("\n📊 最適化統計:")
        
        if 'cache_stats' in stats:
            cache_stats = stats['cache_stats']
            print(f"キャッシュヒット率: {cache_stats['hit_rate']:.1%}")
            print(f"キャッシュサイズ: {cache_stats['size']}/{cache_stats['max_size']}")
        
        if 'batch_stats' in stats:
            batch_stats = stats['batch_stats']
            print(f"バッチ処理数: {batch_stats['total_batches']}")
            print(f"平均バッチサイズ: {batch_stats['average_batch_size']:.1f}")
        
        if 'performance_stats' in stats:
            perf_stats = stats['performance_stats']
            print(f"パフォーマンス監視: {len(perf_stats)}種類の操作を記録")
        
        # 統合結果の表示
        print(f"\n🎯 最適化された統合結果:")
        integrated = result2['integrated_result']
        print(integrated[:400] + "..." if len(integrated) > 400 else integrated)
        
        return result2
        
    finally:
        await client.cleanup()


async def main():
    """メイン実行関数"""
    print("🌟 最適化された圏論的プロンプトエンジニアリング開始")
    
    try:
        result = await demonstrate_optimization()
        
        print("\n" + "=" * 80)
        print("🎉 最適化システム実演完了!")
        print("=" * 80)
        print("✅ バッチ処理・キャッシュ・パフォーマンス最適化を実現!")
        print("🚀 Phase 4: 高度化・最適化 完了!")
        
    except Exception as e:
        logger.error(f"❌ エラー: {e}")
        print("実演中にエラーが発生しました")


if __name__ == "__main__":
    asyncio.run(main())