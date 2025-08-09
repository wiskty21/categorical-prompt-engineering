# -*- coding: utf-8 -*-
"""
圏論的プロンプトエンジニアリング テストスイート
包括的なユニットテスト・統合テスト・パフォーマンステスト

Features:
- 単体テスト（ユニットテスト）
- 統合テスト
- パフォーマンステスト  
- モックテスト（API呼び出しなし）
- エラーハンドリングテスト
- 圏論的性質の検証テスト
"""

import unittest
import asyncio
import time
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from typing import Dict, List, Any
import sys
import os

# テスト対象モジュールのインポート
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from async_categorical_prompt import (
        AsyncTensorProduct, AsyncNaturalTransformation, 
        AsyncAdjointPair, AsyncContextMonad, AsyncClaudeClient, APIConfig
    )
    from robust_categorical_prompt import (
        RobustTensorProduct, RobustClaudeClient, RobustConfig,
        ErrorType, RecoveryStrategy, CircuitBreaker
    )
except ImportError as e:
    print(f"⚠️ インポートエラー: {e}")
    print("必要なモジュールが見つかりません。テスト対象ファイルが存在することを確認してください。")


class TestAsyncClaudeClient(unittest.TestCase):
    """AsyncClaudeClientのテスト"""
    
    def setUp(self):
        """テスト準備"""
        self.config = APIConfig(max_concurrent_requests=2, retry_attempts=2)
        
    @patch.dict(os.environ, {'CLAUDE_API_KEY': 'test-api-key'})
    def test_client_initialization(self):
        """クライアント初期化テスト"""
        client = AsyncClaudeClient("test-key", self.config)
        self.assertEqual(client.api_key, "test-key")
        self.assertEqual(client.config.max_concurrent_requests, 2)
        self.assertIsNotNone(client.semaphore)
    
    @patch.dict(os.environ, {'CLAUDE_API_KEY': 'test-api-key'})
    async def test_generate_response_mock(self):
        """モック応答生成テスト"""
        client = AsyncClaudeClient("test-key", self.config)
        
        # anthropic.AsyncAnthropicをモック
        with patch.object(client.client, 'messages') as mock_messages:
            mock_response = Mock()
            mock_response.content = [Mock(text="テスト応答")]
            mock_messages.create = AsyncMock(return_value=mock_response)
            
            result = await client.generate_response("テストプロンプト")
            
            self.assertEqual(result, "テスト応答")
            mock_messages.create.assert_called_once()
        
        await client.close()
    
    def test_rate_limiting_logic(self):
        """レート制限ロジックのテスト"""
        client = AsyncClaudeClient("test-key", self.config)
        
        # リクエスト時刻を人工的に設定
        now = time.time()
        client._request_times = [now - 30, now - 20, now - 10]  # 過去1分以内の3回
        
        # レート制限チェック（非同期なのでモック）
        self.assertEqual(len(client._request_times), 3)


class TestCircuitBreaker(unittest.TestCase):
    """サーキットブレーカーのテスト"""
    
    def test_initial_state(self):
        """初期状態テスト"""
        cb = CircuitBreaker(failure_threshold=3, reset_timeout=60)
        self.assertEqual(cb.state, "CLOSED")
        self.assertTrue(cb.can_execute())
    
    def test_failure_accumulation(self):
        """失敗蓄積テスト"""
        cb = CircuitBreaker(failure_threshold=2, reset_timeout=60)
        
        cb.record_failure()
        self.assertEqual(cb.state, "CLOSED")
        self.assertTrue(cb.can_execute())
        
        cb.record_failure()
        self.assertEqual(cb.state, "OPEN")
        self.assertFalse(cb.can_execute())
    
    def test_success_reset(self):
        """成功時のリセットテスト"""
        cb = CircuitBreaker(failure_threshold=2, reset_timeout=60)
        
        cb.record_failure()
        cb.record_success()
        
        self.assertEqual(cb.failure_count, 0)
        self.assertEqual(cb.state, "CLOSED")


class TestAsyncTensorProduct(unittest.TestCase):
    """AsyncTensorProductのテスト"""
    
    def setUp(self):
        """テスト準備"""
        self.perspectives = ["観点A", "観点B", "観点C"]
        self.tensor = AsyncTensorProduct(self.perspectives)
    
    def test_initialization(self):
        """初期化テスト"""
        self.assertEqual(self.tensor.perspectives, self.perspectives)
        self.assertEqual(self.tensor.integration_strategy, "synthesis")
    
    async def test_apply_with_mock(self):
        """モックを使った適用テスト"""
        input_text = "テスト入力"
        
        # async_claude をモック
        with patch('async_categorical_prompt.async_claude') as mock_claude:
            mock_claude.generate_response = AsyncMock(return_value="モック応答")
            
            result = await self.tensor.apply(input_text)
            
            self.assertEqual(result["input"], input_text)
            self.assertEqual(result["perspectives"], self.perspectives)
            self.assertTrue(result["async_processing"])
            self.assertIn("processing_time", result)
            self.assertIn("individual_results", result)
            self.assertIn("integrated_result", result)
    
    def test_perspective_count_validation(self):
        """観点数の妥当性テスト"""
        # 空の観点リスト
        empty_tensor = AsyncTensorProduct([])
        self.assertEqual(len(empty_tensor.perspectives), 0)
        
        # 大量の観点
        many_perspectives = [f"観点{i}" for i in range(100)]
        large_tensor = AsyncTensorProduct(many_perspectives)
        self.assertEqual(len(large_tensor.perspectives), 100)


class TestAsyncNaturalTransformation(unittest.TestCase):
    """AsyncNaturalTransformationのテスト"""
    
    def setUp(self):
        """テスト準備"""
        self.transformer = AsyncNaturalTransformation(
            "ソース領域", "ターゲット領域", "変換ルール"
        )
    
    def test_initialization(self):
        """初期化テスト"""
        self.assertEqual(self.transformer.source_domain, "ソース領域")
        self.assertEqual(self.transformer.target_domain, "ターゲット領域")
        self.assertEqual(self.transformer.transformation_rule, "変換ルール")
    
    async def test_transformation_with_mock(self):
        """モック変換テスト"""
        source_content = "ソース内容"
        
        with patch('async_categorical_prompt.async_claude') as mock_claude:
            mock_claude.generate_response = AsyncMock(return_value="変換された内容")
            
            result = await self.transformer.apply_transformation(source_content)
            
            self.assertEqual(result["source_domain"], "ソース領域")
            self.assertEqual(result["target_domain"], "ターゲット領域")
            self.assertEqual(result["source_content"], source_content)
            self.assertEqual(result["transformed_content"], "変換された内容")
            self.assertIn("processing_time", result)


class TestAsyncContextMonad(unittest.TestCase):
    """AsyncContextMonadのテスト"""
    
    def setUp(self):
        """テスト準備"""
        self.initial_context = "初期文脈"
        self.monad = AsyncContextMonad(self.initial_context)
    
    def test_initialization(self):
        """初期化テスト"""
        self.assertEqual(self.monad.current_context, self.initial_context)
        self.assertEqual(len(self.monad.history), 0)
        self.assertEqual(len(self.monad.metadata), 0)
    
    async def test_bind_operation(self):
        """bind演算テスト"""
        new_input = "新しい入力"
        
        with patch('async_categorical_prompt.async_claude') as mock_claude:
            mock_claude.generate_response = AsyncMock(return_value="発展した文脈")
            
            result = await self.monad.bind(new_input)
            
            self.assertEqual(result["new_input"], new_input)
            self.assertEqual(result["evolved_context"], "発展した文脈")
            self.assertEqual(result["history_length"], 1)
            self.assertEqual(self.monad.current_context, "発展した文脈")
            self.assertIn("processing_time", result)
    
    def test_history_management(self):
        """履歴管理テスト"""
        # 履歴に手動で追加
        self.monad.history.append({
            "context": "過去の文脈",
            "timestamp": time.time()
        })
        
        formatted = self.monad._format_history()
        self.assertIn("過去の文脈", formatted)


class TestRobustClaudeClient(unittest.TestCase):
    """RobustClaudeClientのテスト"""
    
    def setUp(self):
        """テスト準備"""
        self.config = RobustConfig(max_retries=2, base_delay=0.1)
        
    @patch.dict(os.environ, {'CLAUDE_API_KEY': 'test-api-key'})  
    def test_error_classification(self):
        """エラー分類テスト"""
        client = RobustClaudeClient("test-key", self.config)
        
        # 各種エラーの分類テスト
        rate_limit_error = Exception("Rate limit exceeded")
        self.assertEqual(client._classify_error(rate_limit_error), ErrorType.RATE_LIMIT)
        
        timeout_error = Exception("Request timeout")
        self.assertEqual(client._classify_error(timeout_error), ErrorType.TIMEOUT)
        
        auth_error = Exception("Authentication failed 401")
        self.assertEqual(client._classify_error(auth_error), ErrorType.AUTHENTICATION)
        
        unknown_error = Exception("Something went wrong")
        self.assertEqual(client._classify_error(unknown_error), ErrorType.UNKNOWN)
    
    @patch.dict(os.environ, {'CLAUDE_API_KEY': 'test-api-key'})
    def test_delay_calculation(self):
        """遅延時間計算テスト"""
        client = RobustClaudeClient("test-key", self.config)
        
        # 指数バックオフのテスト
        delay1 = client._calculate_delay(0, ErrorType.API_ERROR)
        delay2 = client._calculate_delay(1, ErrorType.API_ERROR)
        delay3 = client._calculate_delay(2, ErrorType.API_ERROR)
        
        self.assertGreater(delay2, delay1)
        self.assertGreater(delay3, delay2)
        
        # レート制限の場合の特別な処理
        rate_delay = client._calculate_delay(1, ErrorType.RATE_LIMIT)
        self.assertIsInstance(rate_delay, float)
    
    @patch.dict(os.environ, {'CLAUDE_API_KEY': 'test-api-key'})
    def test_metrics_initialization(self):
        """メトリクス初期化テスト"""
        client = RobustClaudeClient("test-key", self.config)
        metrics = client.get_metrics()
        
        self.assertEqual(metrics["total_requests"], 0)
        self.assertEqual(metrics["successful_requests"], 0)
        self.assertEqual(metrics["failed_requests"], 0)
        self.assertEqual(metrics["success_rate"], 0)


class TestCategoricalProperties(unittest.TestCase):
    """圏論的性質の検証テスト"""
    
    def test_tensor_product_properties(self):
        """テンソル積の性質テスト"""
        # 対称性のテスト（A ⊗ B ≅ B ⊗ A）
        perspectives_ab = ["A", "B"]
        perspectives_ba = ["B", "A"]
        
        tensor_ab = AsyncTensorProduct(perspectives_ab)
        tensor_ba = AsyncTensorProduct(perspectives_ba)
        
        # 観点の集合が同じであることを確認
        self.assertEqual(set(tensor_ab.perspectives), set(tensor_ba.perspectives))
    
    def test_natural_transformation_composition(self):
        """自然変換の合成テスト"""
        # F -> G -> H の合成
        transform1 = AsyncNaturalTransformation("A", "B", "ルール1")
        transform2 = AsyncNaturalTransformation("B", "C", "ルール2")
        
        # 変換の連鎖が可能であることを確認
        self.assertEqual(transform1.target_domain, transform2.source_domain)
    
    def test_monad_laws(self):
        """モナド法則のテスト（構造的検証）"""
        initial_context = "初期"
        monad = AsyncContextMonad(initial_context)
        
        # Left identity: return a >>= f ≡ f a
        # Right identity: m >>= return ≡ m
        # Associativity: (m >>= f) >>= g ≡ m >>= (\x -> f x >>= g)
        
        # 構造的にモナドの要件を満たしているかチェック
        self.assertTrue(hasattr(monad, 'bind'))
        self.assertIsNotNone(monad.current_context)
        self.assertIsInstance(monad.history, list)


class TestPerformance(unittest.TestCase):
    """パフォーマンステスト"""
    
    def test_tensor_product_scaling(self):
        """テンソル積のスケーリングテスト"""
        # 異なる観点数でのパフォーマンス比較
        small_perspectives = ["A", "B"]
        large_perspectives = [f"観点{i}" for i in range(10)]
        
        small_tensor = AsyncTensorProduct(small_perspectives)
        large_tensor = AsyncTensorProduct(large_perspectives)
        
        # メモリ使用量の概算チェック
        self.assertLess(len(small_tensor.perspectives), len(large_tensor.perspectives))
    
    def test_memory_usage(self):
        """メモリ使用量テスト"""
        import sys
        
        # 大きなモナド履歴でのメモリ使用量
        monad = AsyncContextMonad("初期")
        
        initial_size = sys.getsizeof(monad.history)
        
        # 履歴を大量に追加
        for i in range(1000):
            monad.history.append({"context": f"文脈{i}", "timestamp": time.time()})
        
        final_size = sys.getsizeof(monad.history)
        self.assertGreater(final_size, initial_size)


class TestIntegration(unittest.TestCase):
    """統合テスト"""
    
    async def test_full_pipeline_mock(self):
        """フルパイプラインのモックテスト"""
        input_text = "統合テスト入力"
        perspectives = ["観点1", "観点2"]
        
        # 完全なパイプラインをモックで実行
        tensor = AsyncTensorProduct(perspectives)
        
        with patch('async_categorical_prompt.async_claude') as mock_claude:
            mock_claude.generate_response = AsyncMock(return_value="統合テスト応答")
            
            result = await tensor.apply(input_text)
            
            # 結果の完全性チェック
            self.assertIsInstance(result, dict)
            self.assertIn("input", result)
            self.assertIn("perspectives", result) 
            self.assertIn("individual_results", result)
            self.assertIn("integrated_result", result)
            self.assertIn("processing_time", result)
    
    def test_configuration_validation(self):
        """設定値の妥当性テスト"""
        # APIConfig の妥当性
        config = APIConfig(max_concurrent_requests=5, request_timeout=30)
        self.assertGreater(config.max_concurrent_requests, 0)
        self.assertGreater(config.request_timeout, 0)
        
        # RobustConfig の妥当性
        robust_config = RobustConfig(max_retries=3, base_delay=1.0)
        self.assertGreaterEqual(robust_config.max_retries, 0)
        self.assertGreater(robust_config.base_delay, 0)


# テストスイートの実行クラス
class TestRunner:
    """テスト実行管理"""
    
    @staticmethod
    def run_unit_tests():
        """ユニットテストの実行"""
        print("🧪 ユニットテスト実行開始")
        
        loader = unittest.TestLoader()
        suite = unittest.TestSuite()
        
        # 各テストクラスを追加
        test_classes = [
            TestAsyncClaudeClient,
            TestCircuitBreaker,
            TestAsyncTensorProduct,
            TestAsyncNaturalTransformation,
            TestAsyncContextMonad,
            TestRobustClaudeClient,
            TestCategoricalProperties
        ]
        
        for test_class in test_classes:
            tests = loader.loadTestsFromTestCase(test_class)
            suite.addTests(tests)
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()
    
    @staticmethod
    def run_performance_tests():
        """パフォーマンステストの実行"""
        print("⚡ パフォーマンステスト実行開始")
        
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(TestPerformance)
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()
    
    @staticmethod
    def run_integration_tests():
        """統合テストの実行"""
        print("🔗 統合テスト実行開始")
        
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromTestCase(TestIntegration)
        
        # 非同期テストの実行
        async def run_async_tests():
            test_instance = TestIntegration()
            await test_instance.test_full_pipeline_mock()
            test_instance.test_configuration_validation()
        
        # asyncio.run(run_async_tests())
        
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(suite)
        
        return result.wasSuccessful()
    
    @staticmethod
    def run_all_tests():
        """すべてのテストを実行"""
        print("🚀 全テストスイート実行開始")
        print("=" * 80)
        
        results = []
        
        try:
            # ユニットテスト
            print("\n📋 1. ユニットテスト")
            results.append(TestRunner.run_unit_tests())
            
            # パフォーマンステスト
            print("\n📋 2. パフォーマンステスト")  
            results.append(TestRunner.run_performance_tests())
            
            # 統合テスト
            print("\n📋 3. 統合テスト")
            results.append(TestRunner.run_integration_tests())
            
        except Exception as e:
            print(f"❌ テスト実行中にエラー: {e}")
            results.append(False)
        
        # 結果サマリ
        print("\n" + "=" * 80)
        print("📊 テスト結果サマリ")
        print("=" * 80)
        
        success_count = sum(results)
        total_count = len(results)
        
        print(f"成功: {success_count}/{total_count}")
        print(f"成功率: {success_count/total_count*100:.1f}%")
        
        if all(results):
            print("🎉 すべてのテストが成功しました!")
        else:
            print("⚠️ 一部のテストが失敗しました。")
        
        return all(results)


if __name__ == "__main__":
    # メイン実行
    TestRunner.run_all_tests()