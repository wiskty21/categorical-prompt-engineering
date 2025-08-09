# -*- coding: utf-8 -*-
"""
真の圏論的プロンプトエンジニアリング - 実践例

この例では、以下の高度な圏論的概念の実際の威力を示します：
1. 並行合成（テンソル積）- 複数観点の同時適用
2. 構造保存変換（自然変換）- 一貫した領域変換
3. 双対性（アジョイント）- 対立概念の統一
4. 統合最適化（極限・余極限）- 制約満足と創造的統合
5. 文脈保持（モナド）- 履歴を考慮した発展

従来の逐次処理との違いを明確に示します。
"""

from categorical_prompt_advanced import *
import time


def demonstrate_tensor_product_power():
    """テンソル積の威力：並行観点分析"""
    print("=" * 80)
    print("🔥 テンソル積（⊗）の威力 - 並行観点分析")
    print("=" * 80)
    
    # 従来のアプローチ（逐次処理）
    print("\n【従来のアプローチ: 逐次処理】")
    input_text = "人工知能の社会への影響"
    
    start_time = time.time()
    
    # 逐次実行（遅い、文脈が分断される）
    creative_result = "創造的観点: AIは芸術や創作の新しい可能性を開く"
    logical_result = "論理的観点: AIの導入により効率性が向上するが雇用への影響が課題"
    ethical_result = "倫理的観点: AIの判断における透明性と責任の所在が重要"
    
    sequential_time = time.time() - start_time
    print(f"逐次結果（{sequential_time:.3f}秒）:")
    print(f"1. {creative_result}")
    print(f"2. {logical_result}")  
    print(f"3. {ethical_result}")
    print("→ バラバラな分析、統合されていない")
    
    # 圏論的アプローチ（並行テンソル積）
    print("\n【圏論的アプローチ: テンソル積による並行統合】")
    
    start_time = time.time()
    
    # テンソル積で並行実行
    tensor_analysis = create_perspective_tensor(
        "創造的", "論理的", "倫理的", "経済的", "技術的"
    )
    
    tensor_result = tensor_analysis.apply(input_text)
    tensor_time = time.time() - start_time
    
    print(f"テンソル積結果（{tensor_time:.3f}秒）:")
    print(tensor_result)
    print("\n🌟 圏論の威力:")
    print("• 複数観点を同時に適用")
    print("• 観点間の相互作用を考慮")
    print("• 統合された包括的分析")
    print("• 並行処理による効率性")


def demonstrate_natural_transformation_consistency():
    """自然変換による構造保存の威力"""
    print("\n" + "=" * 80)
    print("🔥 自然変換の威力 - 構造を保った一貫変換")
    print("=" * 80)
    
    print("\n【従来のアプローチ: 個別変換（一貫性なし）】")
    
    technical_prompts = [
        "APIの設計原則について分析せよ",
        "データベースの正規化を説明せよ", 
        "アルゴリズムの時間計算量を評価せよ"
    ]
    
    # バラバラな変換（一貫性なし）
    inconsistent_educational = [
        "API設計って何？簡単に教えて",
        "データベースの正規化を初心者向けに説明してください",
        "アルゴリズムの複雑さについて分かりやすく"
    ]
    
    print("個別変換結果:")
    for i, (tech, edu) in enumerate(zip(technical_prompts, inconsistent_educational)):
        print(f"{i+1}. 技術: {tech}")
        print(f"   教育: {edu}")
        print(f"   → 変換の一貫性なし、スタイルがバラバラ")
    
    print("\n【圏論的アプローチ: 自然変換による構造保存】")
    
    # 自然変換の定義
    def technical_to_educational_transform(tech_text: str) -> str:
        """技術文書→教育文書の自然変換"""
        return f"""
初心者学習者向けに構造化された説明:

技術的内容: {tech_text}

学習目標:
1. 基本概念の理解
2. 実際の例による説明  
3. 段階的な習得プロセス
4. 実践的な応用例

分かりやすい説明:
"""
    
    # 自然変換を適用
    print("自然変換結果（構造保存）:")
    for i, tech_prompt in enumerate(technical_prompts):
        edu_result = technical_to_educational_transform(tech_prompt)
        print(f"\n{i+1}. 変換結果:")
        print(edu_result[:200] + "...")
    
    print("\n🌟 自然変換の威力:")
    print("• すべての変換で一貫したスタイル")
    print("• 構造的関係が保持される")
    print("• 予測可能で信頼できる変換")
    print("• 体系的な教育コンテンツ生成")


def demonstrate_adjoint_dialectic():
    """アジョイント関手による双対性の活用"""
    print("\n" + "=" * 80)
    print("🔥 アジョイント関手の威力 - 双対性による創造的統合")
    print("=" * 80)
    
    print("\n【従来のアプローチ: 一方向的思考】")
    
    problem = "環境問題の解決策"
    
    # 一方向的分析（制約的 OR 自由的）
    constrained_analysis = "規制強化と法的制約による環境保護"
    creative_analysis = "技術革新と創造的解決策による環境改善"
    
    print(f"問題: {problem}")
    print(f"制約的アプローチ: {constrained_analysis}")
    print(f"創造的アプローチ: {creative_analysis}")
    print("→ 一方的で対立する解決策、統合されていない")
    
    print("\n【圏論的アプローチ: アジョイント関手による双対統合】")
    
    # アジョイント関手の適用
    adjoint = create_free_forgetful_adjunction()
    
    # 制約→自由化
    liberated = adjoint.free_creative_prompt(constrained_analysis)
    print("制約的 → 自由化:")
    print(liberated)
    
    print("\n" + "-" * 50)
    
    # 自由→制約抽出
    constrained = adjoint.extract_essence(creative_analysis)
    print("創造的 → 本質抽出:")
    print(constrained)
    
    print("\n🌟 アジョイント関手の威力:")
    print("• 対立する概念を統一的に扱える")
    print("• 双方向の変換で洞察を深化")
    print("• 制約と自由の弁証法的統合")
    print("• より豊かで完全な解決策")


def demonstrate_limits_optimization():
    """極限による制約最適化の威力"""
    print("\n" + "=" * 80)
    print("🔥 極限の威力 - 複数制約の同時最適化")
    print("=" * 80)
    
    print("\n【従来のアプローチ: 制約の個別対応】")
    
    project = "新製品開発プロジェクト"
    constraints = ["予算上限500万円", "開発期間6ヶ月", "品質基準ISO準拠", "市場性確保"]
    
    print(f"プロジェクト: {project}")
    print("制約への個別対応:")
    for i, constraint in enumerate(constraints, 1):
        print(f"{i}. {constraint} → 個別の対策を検討")
    print("→ 制約同士の競合や相互作用を考慮できない")
    
    print("\n【圏論的アプローチ: 極限による統合最適化】")
    
    # 極限による制約統合
    constraint_limit = create_constraint_limit(*constraints)
    optimized_solution = constraint_limit.compute_limit(project)
    
    print("極限最適化結果:")
    print(optimized_solution)
    
    print("\n🌟 極限の威力:")
    print("• 全制約を同時に考慮")
    print("• パレート最適解の発見")
    print("• トレードオフの明確化")
    print("• 系統的な最適化")


def demonstrate_monad_context_evolution():
    """モナドによる文脈保持計算の威力"""
    print("\n" + "=" * 80)
    print("🔥 モナドの威力 - 文脈を保った計算")
    print("=" * 80)
    
    print("\n【従来のアプローチ: 文脈を無視した処理】")
    
    conversation = [
        "ユーザー: 機械学習について教えて",
        "AI: 機械学習は...", 
        "ユーザー: それの応用例は？",
        "AI: 応用例として..." # ← 前の文脈を考慮せず
    ]
    
    print("文脈を無視した処理:")
    for turn in conversation:
        print(turn)
    print("→ 各回答が独立、文脈が継承されない")
    
    print("\n【圏論的アプローチ: モナドによる文脈保持】")
    
    # Context Monad で文脈を保持
    initial_prompt = ContextPrompt("機械学習の基本概念を説明してください")
    
    # 文脈を保ちながら会話を発展
    context_prompt1 = initial_prompt.add_context("user_level", "beginner")
    context_prompt2 = context_prompt1.add_context("interest", "practical_applications")
    
    # 履歴を考慮した発展
    evolved_prompt = context_prompt2.evolve_with_history("具体的な応用例について詳しく")
    
    print("文脈保持された発展:")
    print(evolved_prompt)
    
    print("\n🌟 モナドの威力:")
    print("• 会話の文脈を自動保持")
    print("• 履歴を考慮した適切な応答")
    print("• 状態の合成と管理")
    print("• 自然で一貫した対話")


def demonstrate_maybe_monad_robustness():
    """Maybe モナドによる堅牢性の向上"""
    print("\n" + "=" * 80)
    print("🔥 Maybe モナドの威力 - エラー処理の優雅さ")
    print("=" * 80)
    
    print("\n【従来のアプローチ: 例外処理の煩雑さ】")
    
    risky_prompts = [
        "無効な入力データ",
        "適切な技術記事",
        "空文字列データ",
        "正常な分析対象"
    ]
    
    print("例外が発生しやすいプロンプト処理:")
    for prompt in risky_prompts:
        print(f"入力: {prompt}")
        if "無効" in prompt or "空文字列" in prompt:
            print("→ Exception! 処理が中断される")
        else:
            print("→ 正常処理")
    print("→ エラー処理のコードが複雑化")
    
    print("\n【圏論的アプローチ: Maybe モナドによる優雅な処理】")
    
    def safe_analysis(text: str) -> MaybePrompt:
        """失敗の可能性がある分析"""
        maybe = MaybePrompt()
        
        if not text or "無効" in text or "空文字列" in text:
            return maybe.nothing()
        else:
            return maybe.unit(f"分析完了: {text}についての詳細な考察")
    
    def enhance_analysis(maybe_result: MaybePrompt) -> MaybePrompt:
        """分析結果の拡張"""
        return maybe_result.fmap(lambda x: f"拡張された{x}と追加の洞察")
    
    print("Maybe モナドによる安全な処理:")
    for prompt in risky_prompts:
        result = safe_analysis(prompt)
        enhanced = enhance_analysis(result)
        
        print(f"入力: {prompt}")
        print(f"結果: {enhanced.get_or_else('処理不可 - デフォルト応答を使用')}")
        print(f"状態: {enhanced}")
        print()
    
    print("🌟 Maybe モナドの威力:")
    print("• 例外を値として扱う")
    print("• 合成時に自動的にエラー処理")
    print("• コードの簡潔性と堅牢性")
    print("• 予測可能な失敗処理")


def comprehensive_categorical_example():
    """包括的な圏論的プロンプトエンジニアリングの例"""
    print("\n" + "=" * 80)
    print("🚀 包括的圏論的プロンプトエンジニアリング実演")
    print("=" * 80)
    
    problem = "持続可能な都市開発計画"
    
    print(f"\n🎯 課題: {problem}")
    print("\n【圏論的アプローチの統合実演】")
    
    # 1. テンソル積による多角的分析
    print("\n1️⃣ テンソル積 - 並行多角的分析")
    perspectives = create_perspective_tensor(
        "環境保護", "経済発展", "社会福祉", "技術革新", "文化保存"
    )
    multi_perspective = perspectives.apply(problem)
    print("並行分析結果（抜粋）:")
    print(multi_perspective[:300] + "...")
    
    # 2. アジョイント関手による創造的制約統合
    print("\n2️⃣ アジョイント関手 - 制約と創造の統合")
    adjoint = create_free_forgetful_adjunction()
    constrained_view = "法的規制と予算制約内での開発"
    creative_liberation = adjoint.free_creative_prompt(constrained_view)
    print("創造的解放結果（抜粋）:")
    print(creative_liberation[:300] + "...")
    
    # 3. 極限による制約最適化
    print("\n3️⃣ 極限 - 制約最適化")
    constraints = ["環境負荷最小化", "経済効率性", "住民満足度", "技術実現可能性"]
    limit_optimization = create_constraint_limit(*constraints)
    optimized = limit_optimization.compute_limit(problem)
    print("最適化結果（抜粋）:")
    print(optimized[:300] + "...")
    
    # 4. モナドによる文脈保持
    print("\n4️⃣ モナド - 文脈保持発展")
    context_prompt = ContextPrompt(problem)
    context_prompt = context_prompt.add_context("stakeholders", ["市民", "企業", "行政"])
    context_prompt = context_prompt.add_context("timeline", "10年計画")
    evolved = context_prompt.evolve_with_history("実装フェーズの具体的戦略")
    print("文脈考慮発展（抜粋）:")
    print(str(evolved)[:300] + "...")
    
    print("\n🎉 圏論的プロンプトエンジニアリングの総合威力:")
    print("• 複数観点の並行統合 (テンソル積)")
    print("• 対立概念の弁証法的統一 (アジョイント)")
    print("• 複数制約の系統的最適化 (極限)")
    print("• 文脈を保った知的発展 (モナド)")
    print("• 構造的一貫性の保証 (自然変換)")
    print("\n→ 従来の逐次処理を超えた、真に「圏論的」なアプローチ！")


def main():
    """全実演の実行"""
    print("🌟 真の圏論的プロンプトエンジニアリング実演")
    print("vs. 従来の逐次処理アプローチ")
    
    # 各圏論的概念の威力を実演
    demonstrate_tensor_product_power()
    demonstrate_natural_transformation_consistency()  
    demonstrate_adjoint_dialectic()
    demonstrate_limits_optimization()
    demonstrate_monad_context_evolution()
    demonstrate_maybe_monad_robustness()
    
    # 包括的実演
    comprehensive_categorical_example()
    
    print("\n" + "=" * 80)
    print("🎯 結論: 圏論は単なる「理論的美しさ」ではない")
    print("=" * 80)
    print("✨ 実用的価値:")
    print("• 並行処理による効率性")
    print("• 構造保存による信頼性") 
    print("• 双対性による創造性")
    print("• 制約最適化による実用性")
    print("• 文脈保持による知的対話")
    print("\n🚀 これが真の「圏論的プロンプトエンジニアリング」です！")


if __name__ == "__main__":
    main()