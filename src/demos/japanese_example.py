# -*- coding: utf-8 -*-
"""
日本語プロンプトでの圏論的プロンプトエンジニアリング実行例
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from categorical_prompt_engineering import (
    CategoryObject, Morphism, Category, Functor, 
    PromptTemplate, PromptChain
)

def main():
    print("圏論的プロンプトエンジニアリング - 日本語実行例")
    print("=" * 60)
    
    # カテゴリの設定
    category = Category("日本語プロンプトカテゴリ")
    
    # コンテキストオブジェクトの定義
    raw_context = CategoryObject("生データ")
    creative_context = CategoryObject("創作")
    business_context = CategoryObject("ビジネス")
    academic_context = CategoryObject("学術")
    casual_context = CategoryObject("日常会話")
    
    # 日本語プロンプト変換関数の定義
    def to_creative_japanese(text):
        return f"創作活動として、以下のテーマについて想像力豊かに表現してください：{text}"
    
    def to_business_japanese(text):
        return f"ビジネス文書として、以下の内容を専門的に分析してください：{text}"
    
    def to_academic_japanese(text):
        return f"学術論文の観点から、以下のトピックを理論的に考察してください：{text}"
    
    def to_casual_japanese(text):
        return f"友達との会話のように、以下について分かりやすく話してください：{text}"
    
    def summarize_japanese(text):
        return f"以下の内容を3行で要約してください：\n{text}"
    
    def analyze_japanese(text):
        return f"以下の内容を詳しく分析してください：\n{text}"
    
    def make_presentation(text):
        return f"以下の内容をプレゼンテーション資料として構成してください：\n{text}"
    
    # 射（Morphism）の定義
    creative_morph = Morphism(raw_context, creative_context, to_creative_japanese)
    business_morph = Morphism(raw_context, business_context, to_business_japanese)
    academic_morph = Morphism(creative_context, academic_context, to_academic_japanese)
    casual_morph = Morphism(academic_context, casual_context, to_casual_japanese)
    
    # カテゴリに追加
    category.add_object(raw_context)
    category.add_object(creative_context)
    category.add_object(business_context)
    category.add_object(academic_context)
    category.add_object(casual_context)
    
    category.add_morphism(creative_morph)
    category.add_morphism(business_morph)
    category.add_morphism(academic_morph)
    category.add_morphism(casual_morph)
    
    print("\n=== 例1: 基本的な日本語プロンプト変換 ===")
    input_text = "人工知能の未来"
    
    # 創作コンテキストへの変換
    creative_result = creative_morph.apply(input_text)
    print(f"\n入力: {input_text}")
    print(f"創作変換結果:")
    print(creative_result)
    
    print("\n=== 例2: プロンプトの合成（創作→学術→日常会話） ===")
    
    # 合成: 創作 → 学術 → 日常会話
    composed = category.compose(academic_morph, casual_morph)
    if composed:
        final_result = composed.apply(creative_result)
        print(f"\n合成変換結果:")
        print(final_result)
    
    print("\n=== 例3: 日本語プロンプトチェーン ===")
    
    # チェーンの作成（コンテキストを追加で定義）
    analysis_context = CategoryObject("分析")
    summary_context = CategoryObject("要約")
    presentation_context = CategoryObject("プレゼン")
    
    # 射の作成
    analyze_morph = Morphism(raw_context, analysis_context, analyze_japanese)
    summarize_morph = Morphism(analysis_context, summary_context, summarize_japanese)
    present_morph = Morphism(summary_context, presentation_context, make_presentation)
    
    # チェーンの作成
    chain = PromptChain(category)
    chain.add(analyze_morph)
    chain.add(summarize_morph)
    chain.add(present_morph)
    
    topic = "リモートワークの影響と課題"
    chain_result = chain.execute(topic)
    print(f"\n入力トピック: {topic}")
    print(f"チェーン実行結果:")
    print(chain_result)
    
    print("\n=== 例4: 日本語プロンプトテンプレート ===")
    
    # 分析テンプレート
    analysis_template = PromptTemplate(
        "分析テンプレート",
        """以下のトピックについて包括的に分析してください：

トピック: {input}

分析内容:
1. 概要
2. 主要なポイント
3. 課題と機会
4. 結論

詳細な分析:"""
    )
    
    # レポートテンプレート
    report_template = PromptTemplate(
        "レポートテンプレート", 
        """以下の分析結果をビジネスレポートとして整理してください：

{input}

エグゼクティブサマリー:"""
    )
    
    # テンプレートからMorphismを作成
    topic_context = CategoryObject("トピック")
    analysis_context = CategoryObject("分析結果")
    report_context = CategoryObject("レポート")
    
    analysis_morph = analysis_template.create_morphism(topic_context, analysis_context)
    report_morph = report_template.create_morphism(analysis_context, report_context)
    
    topic = "デジタル変革（DX）の現状"
    analysis = analysis_morph.apply(topic)
    print(f"\n分析テンプレート適用結果:")
    print(analysis)
    
    report = report_morph.apply(analysis)
    print(f"\nレポートテンプレート適用結果:")
    print(report)
    
    print("\n=== 例5: 教育的コンテキストへの変換 ===")
    
    # 教育的変換関数
    def to_educational(text):
        return f"初心者向けに分かりやすく説明してください：{text}"
    
    # 教育コンテキスト
    educational_context = CategoryObject("教育")
    educational_morph = Morphism(business_context, educational_context, to_educational)
    
    # 元のビジネスプロンプト
    business_prompt = business_morph.apply("ブロックチェーン技術")
    print(f"\nビジネス向けプロンプト:")
    print(business_prompt)
    
    # 教育的変換
    educational_result = educational_morph.apply(business_prompt)
    print(f"\n教育向け変換結果:")
    print(educational_result)
    
    print("\n=== 例6: 実践的なワークフロー ===")
    
    def brainstorm_japanese(text):
        return f"以下のテーマについてブレインストーミングしてください：\n{text}\n\nアイデア："
    
    def structure_ideas(text):
        return f"以下のアイデアを整理して構造化してください：\n{text}\n\n整理された内容："
    
    def create_action_plan(text):
        return f"以下の内容を基に具体的な行動計画を作成してください：\n{text}\n\nアクションプラン："
    
    # 追加のコンテキストオブジェクト
    idea_context = CategoryObject("アイデア")
    structure_context = CategoryObject("構造化")
    plan_context = CategoryObject("行動計画")
    
    # ワークフローの構築
    brainstorm_morph = Morphism(raw_context, idea_context, brainstorm_japanese)
    structure_morph = Morphism(idea_context, structure_context, structure_ideas)  
    plan_morph = Morphism(structure_context, plan_context, create_action_plan)
    
    # 合成
    workflow = category.compose(brainstorm_morph, structure_morph)
    if workflow:
        complete_workflow = category.compose(workflow, plan_morph)
        if complete_workflow:
            project_topic = "新商品開発プロジェクト"
            workflow_result = complete_workflow.apply(project_topic)
            print(f"\nプロジェクトトピック: {project_topic}")
            print(f"完全ワークフロー結果:")
            print(workflow_result)
    
    print("\n" + "=" * 60)
    print("日本語での圏論的プロンプトエンジニアリング実行完了！")
    print("\n主要な特徴:")
    print("• 日本語コンテキストに適応したプロンプト変換")
    print("• ビジネス・学術・創作・日常会話の各領域間の変換")
    print("• 実践的なワークフローの構築")
    print("• 教育的観点への関手変換")
    print("• テンプレートによる一貫性の確保")

if __name__ == "__main__":
    main()