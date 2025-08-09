# -*- coding: utf-8 -*-
"""
シンプルな圏論的プロンプトエンジニアリング実装
Streamlit Cloud用の軽量版
"""

import anthropic
import asyncio
import time
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

class SimpleCategoricalPrompt:
    """シンプルな圏論的プロンプト処理"""
    
    def __init__(self, api_key: str):
        if not api_key or not api_key.strip():
            raise ValueError("有効なClaude APIキーが必要です")
        self.client = anthropic.Anthropic(api_key=api_key.strip())
    
    def tensor_product_sync(self, input_text: str, perspectives: List[str]) -> Dict[str, Any]:
        """同期版テンソル積（Streamlit Cloud用）"""
        start_time = time.time()
        
        # 個別分析
        individual_results = {}
        for perspective in perspectives:
            prompt = f"""
{perspective}の観点から以下を分析してください:

対象: {input_text}

{perspective}として重要な点:
1. 核心要素
2. 主要課題  
3. 実践的提案

分析結果を300字程度で回答してください:
"""
            try:
                response = self.client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=800,
                    messages=[{"role": "user", "content": prompt}]
                )
                individual_results[perspective] = response.content[0].text
            except Exception as e:
                individual_results[perspective] = f"エラー: {str(e)}"
        
        # 統合分析
        integration_prompt = f"""
以下の多角的分析結果を統合してください:

対象: {input_text}

個別分析:
"""
        
        for perspective, analysis in individual_results.items():
            integration_prompt += f"\n【{perspective}】\n{analysis}\n"
        
        integration_prompt += """
これらの観点を統合し、包括的な結論を400字程度で提示してください:
"""
        
        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1200,
                messages=[{"role": "user", "content": integration_prompt}]
            )
            integrated_result = response.content[0].text
        except Exception as e:
            integrated_result = f"統合エラー: {str(e)}"
        
        end_time = time.time()
        
        return {
            "input": input_text,
            "perspectives": perspectives,
            "individual_results": individual_results,
            "integrated_result": integrated_result,
            "processing_time": end_time - start_time,
            "optimized_processing": False,
            "optimization_stats": None
        }
    
    def natural_transformation_sync(self, content: str, source_domain: str, 
                                  target_domain: str, rule: str) -> Dict[str, Any]:
        """同期版自然変換"""
        start_time = time.time()
        
        prompt = f"""
以下のコンテンツを{source_domain}から{target_domain}に変換してください:

変換ルール: {rule}

元のコンテンツ:
{content}

変換後のコンテンツ:
"""
        
        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}]
            )
            transformed_content = response.content[0].text
        except Exception as e:
            transformed_content = f"変換エラー: {str(e)}"
        
        end_time = time.time()
        
        return {
            "source_domain": source_domain,
            "target_domain": target_domain,
            "transformation_rule": rule,
            "transformed_content": transformed_content,
            "processing_time": end_time - start_time
        }
    
    def adjoint_functor_sync(self, input_text: str) -> Dict[str, Any]:
        """同期版アジョイント関手"""
        start_time = time.time()
        
        # 自由化
        free_prompt = f"""
以下の制約や課題を自由な発想で展開してください:

制約/課題: {input_text}

制約を取り払った場合の可能性や創造的アイデアを提示してください:
"""
        
        try:
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=1000,
                messages=[{"role": "user", "content": free_prompt}]
            )
            free_result = response.content[0].text
        except Exception as e:
            free_result = f"自由化エラー: {str(e)}"
        
        end_time = time.time()
        
        return {
            "result": free_result,
            "processing_time": end_time - start_time
        }
    
    def monad_bind_sync(self, initial_context: str, developments: List[str]) -> Dict[str, Any]:
        """同期版モナド"""
        start_time = time.time()
        current_context = initial_context
        results = []
        
        for development in developments:
            prompt = f"""
現在の文脈: {current_context}

次の発展: {development}

文脈を保持しながら思考を発展させてください:
"""
            
            try:
                response = self.client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=800,
                    messages=[{"role": "user", "content": prompt}]
                )
                evolved_context = response.content[0].text
                current_context = evolved_context
                
                results.append({
                    "new_input": development,
                    "evolved_context": evolved_context,
                    "processing_time": time.time() - start_time
                })
            except Exception as e:
                results.append({
                    "new_input": development,
                    "evolved_context": f"発展エラー: {str(e)}",
                    "processing_time": time.time() - start_time
                })
        
        end_time = time.time()
        
        return {
            "initial_context": initial_context,
            "developments": developments,
            "results": results,
            "final_context": current_context,
            "total_processing_time": end_time - start_time
        }