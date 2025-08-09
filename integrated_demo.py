#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
圏論的プロンプトエンジニアリング 統合デモ
実際の課題解決シナリオでの活用例
"""

import asyncio
import time
from dotenv import load_dotenv
from async_categorical_prompt import (
    AsyncTensorProduct, AsyncNaturalTransformation,
    AsyncAdjointPair, AsyncContextMonad
)

# 環境変数読み込み
load_dotenv()

async def business_analysis_scenario():
    """
    ビジネス分析シナリオ
    新規事業立案における圏論的アプローチ
    """
    print("\n" + "=" * 80)
    print("📊 ビジネス分析シナリオ - 新規事業立案")
    print("=" * 80)
    
    business_idea = "AIを活用した個別化教育サービス"
    
    # Step 1: テンソル積による多角的分析
    print(f"\n【Step 1】多角的分析 (テンソル積)")
    print(f"事業アイデア: {business_idea}")
    
    perspectives = ["市場性", "技術的実現性", "競合優位性", "収益性"]
    tensor = AsyncTensorProduct(perspectives)
    
    print(f"分析観点: {perspectives}")
    print("分析中...")
    
    tensor_result = await tensor.apply(business_idea)
    
    print(f"✅ 分析完了 ({tensor_result['processing_time']:.2f}秒)")
    print("\n統合分析結果（要約）:")
    print(tensor_result['integrated_result'][:400] + "...")
    
    # Step 2: アジョイント関手による制約からの自由化
    print(f"\n【Step 2】創造的発想 (アジョイント関手)")
    
    constraint = "限られた予算と人員で教育サービスを立ち上げる"
    adjoint = AsyncAdjointPair()
    
    print(f"制約条件: {constraint}")
    print("自由化変換中...")
    
    free_result = await adjoint.free_construction(constraint)
    
    print(f"✅ 変換完了 ({free_result['processing_time']:.2f}秒)")
    print("\n創造的アプローチ（要約）:")
    print(free_result['result'][:400] + "...")
    
    # Step 3: モナドによる段階的発展
    print(f"\n【Step 3】実行計画の段階的発展 (モナド)")
    
    initial_plan = "AIを活用した個別化教育サービスの事業化"
    developments = [
        "最小実行可能製品(MVP)の定義",
        "初期ターゲット顧客の特定",
        "パイロットプログラムの設計"
    ]
    
    monad = AsyncContextMonad(initial_plan)
    
    print(f"初期計画: {initial_plan}")
    
    for i, dev in enumerate(developments, 1):
        print(f"\n発展{i}: {dev}")
        result = await monad.bind(dev)
        print(f"結果: {result['evolved_context'][:200]}...")
    
    # Step 4: 自然変換による文書化
    print(f"\n【Step 4】投資家向け資料への変換 (自然変換)")
    
    transformer = AsyncNaturalTransformation(
        "事業計画",
        "投資家向けピッチ",
        "数値・市場機会・成長性を強調、説得力のある表現"
    )
    
    print("変換中...")
    transform_result = await transformer.apply_transformation(monad.current_context[:500])
    
    print(f"✅ 変換完了 ({transform_result['processing_time']:.2f}秒)")
    print("\n投資家向けピッチ（要約）:")
    print(transform_result['transformed_content'][:400] + "...")
    
    print("\n" + "=" * 80)
    print("📊 ビジネス分析完了")
    print("圏論的アプローチにより、多角的分析→創造的発想→段階的計画→効果的プレゼンを実現")
    print("=" * 80)

async def research_scenario():
    """
    研究シナリオ
    学術研究における圏論的アプローチ
    """
    print("\n" + "=" * 80)
    print("🔬 研究シナリオ - 学術研究の発展")
    print("=" * 80)
    
    research_topic = "量子コンピューティングと機械学習の融合"
    
    # Step 1: 文献調査の多角的整理
    print(f"\n【Step 1】文献調査の多角的整理 (テンソル積)")
    
    perspectives = ["理論的基礎", "応用可能性", "技術的課題", "将来展望"]
    tensor = AsyncTensorProduct(perspectives)
    
    print(f"研究テーマ: {research_topic}")
    print(f"調査観点: {perspectives}")
    print("分析中...")
    
    tensor_result = await tensor.apply(research_topic)
    
    print(f"✅ 分析完了 ({tensor_result['processing_time']:.2f}秒)")
    
    # Step 2: 研究仮説の発展
    print(f"\n【Step 2】研究仮説の段階的発展 (モナド)")
    
    initial_hypothesis = "量子アルゴリズムによる機械学習の高速化"
    monad = AsyncContextMonad(initial_hypothesis)
    
    developments = [
        "具体的な量子アルゴリズムの選定",
        "実験設計と評価指標の確立"
    ]
    
    for dev in developments:
        print(f"\n発展: {dev}")
        result = await monad.bind(dev)
        print(f"結果（要約）: {result['evolved_context'][:200]}...")
    
    # Step 3: 学術論文への変換
    print(f"\n【Step 3】学術論文形式への変換 (自然変換)")
    
    transformer = AsyncNaturalTransformation(
        "研究計画",
        "学術論文アブストラクト",
        "学術的な形式、客観的表現、構造化された内容"
    )
    
    print("変換中...")
    transform_result = await transformer.apply_transformation(monad.current_context[:400])
    
    print(f"✅ 変換完了 ({transform_result['processing_time']:.2f}秒)")
    print("\nアブストラクト（要約）:")
    print(transform_result['transformed_content'][:300] + "...")
    
    print("\n" + "=" * 80)
    print("🔬 研究シナリオ完了")
    print("=" * 80)

async def education_scenario():
    """
    教育シナリオ
    教材開発における圏論的アプローチ
    """
    print("\n" + "=" * 80)
    print("📚 教育シナリオ - 教材開発")
    print("=" * 80)
    
    complex_concept = "微分積分の基本定理とその応用"
    
    # Step 1: 概念の多層的理解
    print(f"\n【Step 1】概念の多層的理解 (テンソル積)")
    
    perspectives = ["直感的理解", "厳密な定義", "具体例", "実用的応用"]
    tensor = AsyncTensorProduct(perspectives)
    
    print(f"教育内容: {complex_concept}")
    print(f"理解の層: {perspectives}")
    print("分析中...")
    
    tensor_result = await tensor.apply(complex_concept)
    
    print(f"✅ 分析完了 ({tensor_result['processing_time']:.2f}秒)")
    
    # Step 2: 段階的な学習パス設計
    print(f"\n【Step 2】段階的学習パスの設計 (モナド)")
    
    initial_lesson = "微分積分の基本定理の導入"
    monad = AsyncContextMonad(initial_lesson)
    
    learning_steps = [
        "視覚的な理解を促す例の提示",
        "練習問題による理解の確認"
    ]
    
    for step in learning_steps:
        print(f"\n学習ステップ: {step}")
        result = await monad.bind(step)
        print(f"教材内容（要約）: {result['evolved_context'][:200]}...")
    
    # Step 3: 対象者別の教材変換
    print(f"\n【Step 3】高校生向け教材への変換 (自然変換)")
    
    transformer = AsyncNaturalTransformation(
        "大学レベルの数学",
        "高校生向け教材",
        "数式を最小限に、図解と日常例を多用、段階的理解"
    )
    
    print("変換中...")
    transform_result = await transformer.apply_transformation(
        tensor_result['integrated_result'][:400]
    )
    
    print(f"✅ 変換完了 ({transform_result['processing_time']:.2f}秒)")
    print("\n高校生向け教材（要約）:")
    print(transform_result['transformed_content'][:300] + "...")
    
    print("\n" + "=" * 80)
    print("📚 教育シナリオ完了")
    print("=" * 80)

async def main():
    """メイン実行"""
    print("🌟 圏論的プロンプトエンジニアリング 統合デモ")
    print("実際の課題解決における圏論的アプローチの実演")
    print("=" * 80)
    
    scenarios = {
        "1": ("ビジネス分析", business_analysis_scenario),
        "2": ("研究開発", research_scenario),
        "3": ("教育・学習", education_scenario)
    }
    
    print("\nシナリオを選択してください:")
    print("1. ビジネス分析 - 新規事業立案")
    print("2. 研究開発 - 学術研究の発展")
    print("3. 教育・学習 - 教材開発")
    print("4. すべて実行")
    print("0. 終了")
    
    choice = input("\n選択 (0-4): ").strip()
    
    start_time = time.time()
    
    try:
        if choice == "0":
            print("終了します。")
            return
        elif choice == "4":
            # すべて実行
            for name, scenario_func in scenarios.values():
                print(f"\n{'='*80}")
                print(f"🚀 {name}シナリオ開始")
                await scenario_func()
                print(f"\n✅ {name}シナリオ完了")
        elif choice in scenarios:
            # 個別実行
            name, scenario_func = scenarios[choice]
            await scenario_func()
        else:
            print("無効な選択です。")
            return
            
    except Exception as e:
        print(f"\n❌ エラー: {e}")
    
    total_time = time.time() - start_time
    
    print(f"\n" + "="*80)
    print(f"⏱️  総実行時間: {total_time:.2f}秒")
    print("🎉 統合デモ完了！")
    print("圏論的プロンプトエンジニアリングの実用性を実証しました。")

if __name__ == "__main__":
    asyncio.run(main())