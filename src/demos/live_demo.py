#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
圏論的プロンプトエンジニアリング ライブデモ
実際のClaude APIを使用した動作実演
"""

import asyncio
import os
import time
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

# 自作モジュールのインポート
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from async_categorical_prompt import (
    AsyncTensorProduct, AsyncNaturalTransformation,
    AsyncAdjointPair, AsyncContextMonad
)

async def demo_tensor_product():
    """テンソル積のライブデモ"""
    print("\n" + "=" * 60)
    print("⊗ テンソル積デモ - 並行多観点分析")
    print("=" * 60)
    
    input_text = "人工知能が社会に与える影響"
    perspectives = ["技術的観点", "倫理的観点", "経済的観点"]
    
    print(f"入力: {input_text}")
    print(f"観点: {perspectives}")
    print("\n分析中...")
    
    tensor = AsyncTensorProduct(perspectives)
    start_time = time.time()
    
    try:
        result = await tensor.apply(input_text)
        
        print(f"\n✅ 処理完了 (処理時間: {result['processing_time']:.2f}秒)")
        print("\n【統合結果】")
        print("-" * 40)
        print(result['integrated_result'][:500] + "..." if len(result['integrated_result']) > 500 else result['integrated_result'])
        
        return True
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

async def demo_natural_transformation():
    """自然変換のライブデモ"""
    print("\n" + "=" * 60)
    print("🔄 自然変換デモ - 構造保存変換")
    print("=" * 60)
    
    content = "機械学習は大量のデータからパターンを学習するアルゴリズムです。"
    
    print(f"元の内容: {content}")
    print("変換: 技術文書 → 子供向け説明")
    print("\n変換中...")
    
    transformer = AsyncNaturalTransformation(
        "技術文書",
        "子供向け説明",
        "専門用語を使わず、身近な例えで説明"
    )
    
    try:
        result = await transformer.apply_transformation(content)
        
        print(f"\n✅ 処理完了 (処理時間: {result['processing_time']:.2f}秒)")
        print("\n【変換結果】")
        print("-" * 40)
        print(result['transformed_content'])
        
        return True
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

async def demo_adjoint():
    """アジョイント関手のライブデモ"""
    print("\n" + "=" * 60)
    print("🔄 アジョイント関手デモ - 自由化と本質抽出")
    print("=" * 60)
    
    constrained_input = "効率的なコスト削減を実現するための施策"
    
    print(f"制約的入力: {constrained_input}")
    print("\n自由化変換実行中...")
    
    adjoint = AsyncAdjointPair()
    
    try:
        result = await adjoint.free_construction(constrained_input)
        
        print(f"\n✅ 処理完了 (処理時間: {result['processing_time']:.2f}秒)")
        print("\n【自由化結果】")
        print("-" * 40)
        print(result['result'][:400] + "..." if len(result['result']) > 400 else result['result'])
        
        return True
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

async def demo_monad():
    """モナドのライブデモ"""
    print("\n" + "=" * 60)
    print("🧠 モナドデモ - 文脈保持発展")
    print("=" * 60)
    
    initial_context = "新しいアプリケーションの開発を検討している"
    developments = [
        "ユーザーのニーズを調査したい",
        "技術スタックを決定する必要がある"
    ]
    
    print(f"初期文脈: {initial_context}")
    print(f"発展ステップ: {developments}")
    print("\n文脈発展中...")
    
    monad = AsyncContextMonad(initial_context)
    
    try:
        for i, dev in enumerate(developments, 1):
            print(f"\nステップ {i}: {dev}")
            result = await monad.bind(dev)
            print(f"発展結果: {result['evolved_context'][:200]}...")
        
        print(f"\n✅ 処理完了")
        print("\n【最終文脈】")
        print("-" * 40)
        print(monad.current_context[:400] + "..." if len(monad.current_context) > 400 else monad.current_context)
        
        return True
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

async def main():
    """メインデモ実行"""
    print("🚀 圏論的プロンプトエンジニアリング ライブデモ")
    print("実際のClaude APIを使用した動作実演")
    print("=" * 60)
    
    demos = [
        ("テンソル積", demo_tensor_product),
        ("自然変換", demo_natural_transformation),
        ("アジョイント関手", demo_adjoint),
        ("モナド", demo_monad)
    ]
    
    print("\n実行するデモを選択してください:")
    print("1. テンソル積 (並行多観点分析)")
    print("2. 自然変換 (構造保存変換)")
    print("3. アジョイント関手 (自由化と本質抽出)")
    print("4. モナド (文脈保持発展)")
    print("5. すべて実行")
    print("0. 終了")
    
    try:
        choice = input("\n選択 (0-5): ").strip()
        
        if choice == "0":
            print("終了します。")
            return
        elif choice == "5":
            # すべて実行
            for name, demo_func in demos:
                success = await demo_func()
                if not success:
                    print(f"\n⚠️ {name}でエラーが発生しました")
        elif choice in ["1", "2", "3", "4"]:
            # 個別実行
            idx = int(choice) - 1
            name, demo_func = demos[idx]
            await demo_func()
        else:
            print("無効な選択です。")
    
    except KeyboardInterrupt:
        print("\n\n中断されました。")
    except Exception as e:
        print(f"\n❌ エラー: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 デモ完了！")
    print("圏論的プロンプトエンジニアリングの威力をご確認いただけました。")

if __name__ == "__main__":
    print("⚠️ 注意: このデモは実際のClaude APIを使用します。")
    print("API使用量に応じて課金が発生する可能性があります。")
    
    import sys
    if sys.stdin.isatty():
        confirm = input("続行しますか？ (y/N): ").strip().lower()
        if confirm != 'y':
            print("キャンセルしました。")
            sys.exit(0)
    else:
        print("非インタラクティブモード: 自動実行開始...")
    
    asyncio.run(main())