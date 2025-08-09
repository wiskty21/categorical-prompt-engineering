#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Claude API接続テスト
APIキーの動作確認用スクリプト
"""

import asyncio
import os
from dotenv import load_dotenv
import anthropic

# 環境変数読み込み
load_dotenv()
CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")

async def test_claude_connection():
    """Claude API接続テスト"""
    print("🔌 Claude API接続テスト開始...")
    
    try:
        # クライアント作成
        client = anthropic.AsyncAnthropic(api_key=CLAUDE_API_KEY)
        
        # シンプルなテストメッセージ
        response = await client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=100,
            messages=[
                {"role": "user", "content": "こんにちは。これはテストメッセージです。簡潔に応答してください。"}
            ]
        )
        
        print("✅ API接続成功！")
        print(f"応答: {response.content[0].text}")
        
        await client.aclose()
        return True
        
    except Exception as e:
        print(f"❌ API接続エラー: {e}")
        return False

async def test_tensor_product_simple():
    """シンプルなテンソル積テスト"""
    print("\n⊗ テンソル積の簡易テスト...")
    
    try:
        from async_categorical_prompt import AsyncClaudeClient, APIConfig
        
        config = APIConfig(max_concurrent_requests=2, retry_attempts=1)
        client = AsyncClaudeClient(CLAUDE_API_KEY, config)
        
        # 簡単なプロンプトでテスト
        result = await client.generate_response(
            "AIの利点を一つ挙げてください。",
            max_tokens=50
        )
        
        print("✅ テンソル積コンポーネント動作確認")
        print(f"応答の長さ: {len(result)} 文字")
        
        await client.close()
        return True
        
    except Exception as e:
        print(f"❌ テンソル積テストエラー: {e}")
        return False

async def main():
    """メインテスト実行"""
    print("🧪 圏論的プロンプトエンジニアリング API動作確認")
    print("=" * 60)
    
    # 1. API接続テスト
    connection_ok = await test_claude_connection()
    
    # 2. コンポーネントテスト
    component_ok = await test_tensor_product_simple()
    
    print("\n" + "=" * 60)
    print("📊 テスト結果サマリ")
    print(f"API接続: {'✅ 成功' if connection_ok else '❌ 失敗'}")
    print(f"コンポーネント: {'✅ 成功' if component_ok else '❌ 失敗'}")
    
    if connection_ok and component_ok:
        print("\n🎉 すべてのテストが成功しました！")
        print("圏論的プロンプトエンジニアリングが利用可能です。")
    else:
        print("\n⚠️ 一部のテストが失敗しました。")

if __name__ == "__main__":
    asyncio.run(main())