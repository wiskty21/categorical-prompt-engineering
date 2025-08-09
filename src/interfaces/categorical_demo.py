#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
圏論的プロンプトエンジニアリング Webデモサイト
Streamlitを使用したブラウザベースのインタラクティブUI

ブラウザで圏論的プロンプトエンジニアリングを体験できるデモサイト
教育・研究・実用の全てをカバー
"""

import streamlit as st
import asyncio
import time
import json
import os
import sys
from typing import Dict, List, Any, Optional
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from datetime import datetime
import base64

# 自作モジュールのインポート
try:
    import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from optimized_categorical_prompt import (
        OptimizedTensorProduct, OptimizedClaudeClient, OptimizationConfig
    )
    import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from async_categorical_prompt import (
        AsyncNaturalTransformation, AsyncAdjointPair, AsyncContextMonad
    )
    import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'core'))

from robust_categorical_prompt import RobustConfig
except ImportError as e:
    st.error(f"必要なモジュールが見つかりません: {e}")
    st.stop()

# ページ設定
st.set_page_config(
    page_title="圏論的プロンプトエンジニアリング",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-org/categorical-prompt-engineering',
        'Report a bug': 'https://github.com/your-org/categorical-prompt-engineering/issues',
        'About': "圏論的プロンプトエンジニアリング - 数学の美しさと実用的価値の融合"
    }
)

# カスタムCSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .category-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        margin: 0.25rem;
        background-color: #e8f4fd;
        color: #1f77b4;
        border-radius: 1rem;
        font-size: 0.8rem;
        font-weight: bold;
    }
    .result-container {
        background-color: #f8f9fa;
        border-radius: 0.5rem;
        padding: 1.5rem;
        margin: 1rem 0;
        border-left: 4px solid #1f77b4;
    }
    .performance-metric {
        text-align: center;
        padding: 1rem;
        background-color: #e8f5e8;
        border-radius: 0.5rem;
        margin: 0.5rem;
    }
    .error-message {
        background-color: #ffe6e6;
        border: 1px solid #ff9999;
        border-radius: 0.5rem;
        padding: 1rem;
        color: #cc0000;
    }
</style>
""", unsafe_allow_html=True)


class StreamlitCategoricalUI:
    """Streamlit UI管理クラス"""
    
    def __init__(self):
        self.initialize_session_state()
        self.client = None
    
    def initialize_session_state(self):
        """セッション状態初期化"""
        defaults = {
            'api_key': '',
            'processing': False,
            'results_history': [],
            'current_operation': None,
            'performance_stats': {},
            'user_preferences': {
                'theme': 'light',
                'auto_cache': True,
                'detailed_output': True
            }
        }
        
        for key, default_value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = default_value
    
    async def get_client(self) -> Optional[OptimizedClaudeClient]:
        """最適化クライアント取得"""
        if not st.session_state.api_key:
            st.error("🔑 Claude APIキーを入力してください")
            return None
        
        if self.client is None:
            try:
                config = OptimizationConfig()
                self.client = OptimizedClaudeClient(st.session_state.api_key, config)
            except Exception as e:
                st.error(f"❌ クライアント初期化エラー: {e}")
                return None
        
        return self.client
    
    def render_header(self):
        """ヘッダー描画"""
        st.markdown('<h1 class="main-header">🧮 圏論的プロンプトエンジニアリング</h1>', 
                   unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; color: #666; margin-bottom: 2rem;">
            数学の美しさと実用的価値を融合した革新的なプロンプト処理システム<br>
            <strong>Category Theory meets AI Engineering</strong>
        </div>
        """, unsafe_allow_html=True)
    
    def render_sidebar(self):
        """サイドバー描画"""
        with st.sidebar:
            st.header("⚙️ 設定")
            
            # API キー入力
            st.subheader("🔑 認証")
            api_key = st.text_input(
                "Claude API Key",
                type="password",
                value=st.session_state.api_key,
                help="Claude APIキーを入力してください"
            )
            
            if api_key != st.session_state.api_key:
                st.session_state.api_key = api_key
                self.client = None  # クライアントをリセット
            
            # 設定オプション
            st.subheader("🎛️ オプション")
            
            st.session_state.user_preferences['auto_cache'] = st.checkbox(
                "自動キャッシュ",
                value=st.session_state.user_preferences['auto_cache'],
                help="結果をキャッシュして高速化"
            )
            
            st.session_state.user_preferences['detailed_output'] = st.checkbox(
                "詳細出力", 
                value=st.session_state.user_preferences['detailed_output'],
                help="詳細な分析結果と統計を表示"
            )
            
            # 操作履歴
            st.subheader("📋 操作履歴")
            if st.session_state.results_history:
                for i, result in enumerate(reversed(st.session_state.results_history[-5:])):
                    with st.expander(f"{result.get('operation', 'Unknown')} - {result.get('timestamp', 'No time')}"):
                        st.write(f"処理時間: {result.get('processing_time', 0):.2f}秒")
                        st.write(f"入力: {result.get('input_text', 'N/A')[:100]}...")
            else:
                st.info("まだ操作履歴がありません")
            
            # クリアボタン
            if st.button("履歴をクリア"):
                st.session_state.results_history = []
                st.rerun()
    
    def render_tensor_product_tab(self):
        """テンソル積タブ"""
        st.header("⊗ テンソル積 (Tensor Product)")
        st.markdown("""
        複数の観点から同時に分析し、結果を統合します。
        圏論における**テンソル積**の概念を活用した並行処理です。
        """)
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            input_text = st.text_area(
                "分析対象テキスト",
                height=100,
                placeholder="ここに分析したいテキストを入力してください..."
            )
        
        with col2:
            st.subheader("観点選択")
            
            # プリセット観点
            preset_perspectives = {
                "ビジネス分析": ["戦略", "財務", "マーケティング", "運用", "リスク"],
                "技術評価": ["技術", "セキュリティ", "スケーラビリティ", "保守性", "パフォーマンス"],
                "社会的影響": ["社会", "環境", "倫理", "法的", "文化"],
                "教育的観点": ["教育学", "心理学", "認知科学", "学習理論", "評価"]
            }
            
            selected_preset = st.selectbox(
                "プリセット観点",
                ["カスタム"] + list(preset_perspectives.keys())
            )
            
            if selected_preset != "カスタム":
                perspectives = preset_perspectives[selected_preset]
                st.info(f"選択された観点: {', '.join(perspectives)}")
            else:
                custom_perspectives = st.text_input(
                    "カスタム観点（カンマ区切り）",
                    value="技術,ビジネス,ユーザー,セキュリティ"
                )
                perspectives = [p.strip() for p in custom_perspectives.split(",") if p.strip()]
        
        if st.button("🚀 テンソル積実行", type="primary", disabled=st.session_state.processing):
            if not input_text:
                st.warning("分析対象テキストを入力してください")
            elif not perspectives:
                st.warning("観点を選択してください")
            else:
                asyncio.run(self.execute_tensor_product(input_text, perspectives))
    
    async def execute_tensor_product(self, input_text: str, perspectives: List[str]):
        """テンソル積実行"""
        client = await self.get_client()
        if not client:
            return
        
        st.session_state.processing = True
        
        try:
            with st.spinner('🔄 テンソル積を実行中...'):
                tensor = OptimizedTensorProduct(perspectives, client=client)
                
                start_time = time.time()
                result = await tensor.apply(
                    input_text,
                    use_cache=st.session_state.user_preferences['auto_cache'],
                    use_batch=True
                )
                
                # 結果表示
                self.display_tensor_result(result, input_text, perspectives)
                
                # 履歴に追加
                self.add_to_history("tensor", input_text, result, start_time)
                
        except Exception as e:
            st.error(f"❌ エラーが発生しました: {e}")
        
        finally:
            st.session_state.processing = False
    
    def display_tensor_result(self, result: Dict[str, Any], input_text: str, perspectives: List[str]):
        """テンソル積結果表示"""
        st.success("✅ テンソル積実行完了！")
        
        # パフォーマンス指標
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="performance-metric">', unsafe_allow_html=True)
            st.metric("処理時間", f"{result.get('processing_time', 0):.2f}秒")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="performance-metric">', unsafe_allow_html=True)
            st.metric("観点数", len(perspectives))
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="performance-metric">', unsafe_allow_html=True)
            if 'optimization_stats' in result and 'cache_stats' in result['optimization_stats']:
                hit_rate = result['optimization_stats']['cache_stats'].get('hit_rate', 0)
                st.metric("キャッシュ率", f"{hit_rate:.1%}")
            else:
                st.metric("キャッシュ率", "N/A")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="performance-metric">', unsafe_allow_html=True)
            st.metric("最適化", "有効" if result.get('optimized_processing') else "無効")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 統合結果
        st.subheader("🎯 統合結果")
        with st.container():
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            st.write(result.get('integrated_result', 'No integrated result'))
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 個別分析結果
        if st.session_state.user_preferences['detailed_output']:
            st.subheader("🔍 個別分析結果")
            
            individual_results = result.get('individual_results', {})
            for perspective, analysis in individual_results.items():
                with st.expander(f"【{perspective}の観点】"):
                    if analysis.startswith("エラー"):
                        st.markdown(f'<div class="error-message">{analysis}</div>', 
                                  unsafe_allow_html=True)
                    else:
                        st.write(analysis)
        
        # 観点分布の可視化
        if len(perspectives) > 1:
            st.subheader("📊 分析観点の分布")
            
            # 各観点の文字数を計算
            individual_results = result.get('individual_results', {})
            perspective_lengths = []
            
            for perspective in perspectives:
                analysis = individual_results.get(perspective, "")
                if not analysis.startswith("エラー"):
                    perspective_lengths.append({
                        "観点": perspective,
                        "文字数": len(analysis),
                        "ステータス": "成功"
                    })
                else:
                    perspective_lengths.append({
                        "観点": perspective, 
                        "文字数": 0,
                        "ステータス": "エラー"
                    })
            
            if perspective_lengths:
                df = pd.DataFrame(perspective_lengths)
                
                fig = px.bar(
                    df, 
                    x="観点", 
                    y="文字数",
                    color="ステータス",
                    title="観点別分析結果の長さ"
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
    
    def render_natural_transformation_tab(self):
        """自然変換タブ"""
        st.header("🔄 自然変換 (Natural Transformation)")
        st.markdown("""
        一つの領域から別の領域への構造保存変換を行います。
        圏論の**自然変換**により、本質を保ちながら表現形式を変更します。
        """)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            content = st.text_area(
                "変換対象コンテンツ",
                height=150,
                placeholder="ここに変換したいコンテンツを入力してください..."
            )
        
        with col2:
            st.subheader("変換設定")
            
            # プリセット変換
            transformations = {
                "技術文書 → 初心者向け": ("技術文書", "初心者向け教材", "専門用語を平易に、概念を具体例で説明"),
                "学術論文 → 実用ガイド": ("学術論文", "実用ガイド", "理論を実践的応用に、研究成果を使える形に変換"),
                "ビジネス文書 → 技術仕様": ("ビジネス文書", "技術仕様", "ビジネス要求を技術仕様に、抽象概念を実装可能に変換"),
                "堅い文章 → カジュアル": ("堅い文章", "カジュアル文章", "堅い表現をフレンドリーに、親しみやすく変換")
            }
            
            selected_transformation = st.selectbox(
                "変換プリセット",
                ["カスタム"] + list(transformations.keys())
            )
            
            if selected_transformation != "カスタム":
                source, target, rule = transformations[selected_transformation]
                st.info(f"{source} → {target}")
            else:
                source = st.text_input("変換元領域", value="技術文書")
                target = st.text_input("変換先領域", value="一般向け記事")
                rule = st.text_area("変換ルール", value="分かりやすく、具体的に変換")
        
        if st.button("🔄 自然変換実行", type="primary", disabled=st.session_state.processing):
            if not content:
                st.warning("変換対象コンテンツを入力してください")
            else:
                asyncio.run(self.execute_natural_transformation(content, source, target, rule))
    
    async def execute_natural_transformation(self, content: str, source: str, target: str, rule: str):
        """自然変換実行"""
        client = await self.get_client()
        if not client:
            return
        
        st.session_state.processing = True
        
        try:
            with st.spinner('🔄 自然変換を実行中...'):
                transformer = AsyncNaturalTransformation(source, target, rule)
                
                start_time = time.time()
                result = await transformer.apply_transformation(content)
                
                # 結果表示
                self.display_transformation_result(result, content)
                
                # 履歴に追加
                self.add_to_history("transform", content, result, start_time)
                
        except Exception as e:
            st.error(f"❌ エラーが発生しました: {e}")
        
        finally:
            st.session_state.processing = False
    
    def display_transformation_result(self, result: Dict[str, Any], original_content: str):
        """変換結果表示"""
        st.success("✅ 自然変換完了！")
        
        # 変換情報
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("処理時間", f"{result.get('processing_time', 0):.2f}秒")
        
        with col2:
            st.metric("元の文字数", len(original_content))
        
        with col3:
            transformed = result.get('transformed_content', '')
            st.metric("変換後文字数", len(transformed))
        
        # 変換前後の比較
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"📄 変換前 ({result.get('source_domain', 'Unknown')})")
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            st.write(original_content)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.subheader(f"📝 変換後 ({result.get('target_domain', 'Unknown')})")
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            st.write(result.get('transformed_content', 'No transformation result'))
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 変換ルール表示
        if st.session_state.user_preferences['detailed_output']:
            st.subheader("⚙️ 変換ルール")
            st.info(result.get('transformation_rule', 'No rule specified'))
    
    def render_adjoint_tab(self):
        """アジョイント関手タブ"""
        st.header("🔄 アジョイント関手 (Adjoint Functors)")
        st.markdown("""
        制約からの**自由化**と**本質抽出**の双対性を活用します。
        Free ⊣ Forgetful の随伴関係により創造性と実用性を両立させます。
        """)
        
        input_text = st.text_area(
            "入力テキスト（制約条件や課題）",
            height=100,
            placeholder="制約条件や解決したい課題を入力してください..."
        )
        
        cycle_mode = st.checkbox(
            "完全サイクル実行",
            help="制約 → 自由化 → 本質抽出の完全サイクルを実行"
        )
        
        if st.button("🔄 アジョイント関手実行", type="primary", disabled=st.session_state.processing):
            if not input_text:
                st.warning("入力テキストを入力してください")
            else:
                asyncio.run(self.execute_adjoint(input_text, cycle_mode))
    
    async def execute_adjoint(self, input_text: str, cycle_mode: bool):
        """アジョイント関手実行"""
        st.session_state.processing = True
        
        try:
            with st.spinner('🔄 アジョイント関手を実行中...'):
                adjoint = AsyncAdjointPair()
                
                start_time = time.time()
                if cycle_mode:
                    result = await adjoint.adjoint_cycle(input_text)
                else:
                    result = await adjoint.free_construction(input_text)
                
                # 結果表示
                self.display_adjoint_result(result, input_text, cycle_mode)
                
                # 履歴に追加
                self.add_to_history("adjoint", input_text, result, start_time)
                
        except Exception as e:
            st.error(f"❌ エラーが発生しました: {e}")
        
        finally:
            st.session_state.processing = False
    
    def display_adjoint_result(self, result: Dict[str, Any], input_text: str, cycle_mode: bool):
        """アジョイント関手結果表示"""
        st.success("✅ アジョイント関手実行完了！")
        
        if cycle_mode and 'cycle_complete' in result:
            # サイクルモード
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("🆓 自由化結果")
                st.markdown('<div class="result-container">', unsafe_allow_html=True)
                free_result = result.get('free_construction', {}).get('result', 'No free construction result')
                st.write(free_result)
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                st.subheader("📝 本質抽出結果")
                st.markdown('<div class="result-container">', unsafe_allow_html=True)
                forgetful_result = result.get('forgetful_extraction', {}).get('result', 'No forgetful extraction result')
                st.write(forgetful_result)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # 処理時間
            free_time = result.get('free_construction', {}).get('processing_time', 0)
            forgetful_time = result.get('forgetful_extraction', {}).get('processing_time', 0)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("自由化時間", f"{free_time:.2f}秒")
            with col2:
                st.metric("抽出時間", f"{forgetful_time:.2f}秒")
            with col3:
                st.metric("総処理時間", f"{free_time + forgetful_time:.2f}秒")
        
        else:
            # 単一実行モード
            st.subheader("🆓 自由化結果")
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            st.write(result.get('result', 'No result'))
            st.markdown('</div>', unsafe_allow_html=True)
            
            st.metric("処理時間", f"{result.get('processing_time', 0):.2f}秒")
    
    def render_monad_tab(self):
        """モナドタブ"""
        st.header("🧠 モナド (Monad)")
        st.markdown("""
        文脈を保持しながら段階的に思考を発展させます。
        モナドの**bind**操作により一貫した文脈での連続的な思考発展を実現します。
        """)
        
        initial_context = st.text_area(
            "初期文脈",
            height=80,
            placeholder="思考の出発点となる初期文脈を入力してください..."
        )
        
        st.subheader("発展ステップ")
        
        # 動的な発展ステップ入力
        if 'development_steps' not in st.session_state:
            st.session_state.development_steps = [""]
        
        for i, step in enumerate(st.session_state.development_steps):
            col1, col2 = st.columns([5, 1])
            with col1:
                new_step = st.text_input(f"ステップ {i+1}", value=step, key=f"step_{i}")
                st.session_state.development_steps[i] = new_step
            with col2:
                if st.button("🗑️", key=f"delete_{i}") and len(st.session_state.development_steps) > 1:
                    st.session_state.development_steps.pop(i)
                    st.rerun()
        
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("➕ ステップ追加"):
                st.session_state.development_steps.append("")
                st.rerun()
        
        with col2:
            if st.button("🧠 モナド実行", type="primary", disabled=st.session_state.processing):
                valid_steps = [step for step in st.session_state.development_steps if step.strip()]
                if not initial_context:
                    st.warning("初期文脈を入力してください")
                elif not valid_steps:
                    st.warning("少なくとも1つの発展ステップを入力してください")
                else:
                    asyncio.run(self.execute_monad(initial_context, valid_steps))
    
    async def execute_monad(self, initial_context: str, developments: List[str]):
        """モナド実行"""
        st.session_state.processing = True
        
        try:
            with st.spinner('🧠 モナド発展を実行中...'):
                monad = AsyncContextMonad(initial_context)
                
                start_time = time.time()
                results = []
                
                for i, development in enumerate(developments, 1):
                    st.info(f"ステップ {i}/{len(developments)}: {development}")
                    result = await monad.bind(development)
                    results.append(result)
                
                # 全体結果の構築
                monad_result = {
                    "initial_context": initial_context,
                    "developments": developments,
                    "results": results,
                    "final_context": monad.current_context,
                    "total_processing_time": time.time() - start_time
                }
                
                # 結果表示
                self.display_monad_result(monad_result)
                
                # 履歴に追加
                self.add_to_history("monad", initial_context, monad_result, start_time)
                
        except Exception as e:
            st.error(f"❌ エラーが発生しました: {e}")
        
        finally:
            st.session_state.processing = False
    
    def display_monad_result(self, result: Dict[str, Any]):
        """モナド結果表示"""
        st.success("✅ モナド発展完了！")
        
        # 統計表示
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("総処理時間", f"{result.get('total_processing_time', 0):.2f}秒")
        
        with col2:
            st.metric("発展ステップ数", len(result.get('results', [])))
        
        with col3:
            avg_time = result.get('total_processing_time', 0) / len(result.get('results', [1]))
            st.metric("平均ステップ時間", f"{avg_time:.2f}秒")
        
        # 発展過程の表示
        st.subheader("🧠 思考の発展過程")
        
        # 初期文脈
        st.markdown("**初期文脈:**")
        st.markdown('<div class="result-container">', unsafe_allow_html=True)
        st.write(result.get('initial_context', ''))
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 各ステップの結果
        for i, step_result in enumerate(result.get('results', []), 1):
            st.markdown(f"**ステップ {i}:** {step_result.get('new_input', '')}")
            st.markdown('<div class="result-container">', unsafe_allow_html=True)
            st.write(step_result.get('evolved_context', ''))
            st.markdown('</div>', unsafe_allow_html=True)
        
        # 最終文脈
        st.subheader("🎯 最終的な発展結果")
        st.markdown('<div class="result-container">', unsafe_allow_html=True)
        st.write(result.get('final_context', ''))
        st.markdown('</div>', unsafe_allow_html=True)
        
        # 発展の可視化
        if st.session_state.user_preferences['detailed_output']:
            st.subheader("📊 発展過程の可視化")
            
            step_data = []
            for i, step_result in enumerate(result.get('results', []), 1):
                step_data.append({
                    "ステップ": f"ステップ{i}",
                    "処理時間": step_result.get('processing_time', 0),
                    "文脈長": len(step_result.get('evolved_context', ''))
                })
            
            if step_data:
                df = pd.DataFrame(step_data)
                
                col1, col2 = st.columns(2)
                
                with col1:
                    fig1 = px.bar(df, x="ステップ", y="処理時間", title="ステップ別処理時間")
                    st.plotly_chart(fig1, use_container_width=True)
                
                with col2:
                    fig2 = px.line(df, x="ステップ", y="文脈長", title="文脈の発展", markers=True)
                    st.plotly_chart(fig2, use_container_width=True)
    
    def add_to_history(self, operation: str, input_text: str, result: Dict[str, Any], start_time: float):
        """履歴に追加"""
        history_entry = {
            "operation": operation,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "input_text": input_text[:100] + "..." if len(input_text) > 100 else input_text,
            "processing_time": result.get('processing_time', time.time() - start_time),
            "success": True
        }
        
        st.session_state.results_history.append(history_entry)
        
        # 履歴の上限管理
        if len(st.session_state.results_history) > 50:
            st.session_state.results_history = st.session_state.results_history[-25:]
    
    def render_about_tab(self):
        """aboutタブ"""
        st.header("🧮 圏論的プロンプトエンジニアリングについて")
        
        st.markdown("""
        ### 🎯 プロジェクトの目的
        
        圏論的プロンプトエンジニアリングは、**数学の美しさと実用的価値を融合**した革新的なAI対話システムです。
        圏論（Category Theory）の数学的概念を活用し、従来のプロンプトエンジニアリングを超越したシステムを実現しています。
        
        ### 🔬 核心となる圏論的概念
        
        """)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            #### ⊗ テンソル積 (Tensor Product)
            複数の観点を**真の並行処理**で同時分析し、結果を統合します。
            単純な逐次処理を超えた、数学的に厳密な並行合成を実現。
            
            #### 🔄 自然変換 (Natural Transformation)
            領域間の**構造保存変換**により、本質を維持しながら表現形式を変更。
            単なる翻訳ではなく、数学的な構造保存による高品質な変換。
            """)
        
        with col2:
            st.markdown("""
            #### 🔄 アジョイント関手 (Adjoint Functors)
            Free ⊣ Forgetful の**双対性**により、創造的自由化と実用的本質抽出を両立。
            制約からの解放と核心の凝縮という対極的操作の数学的統合。
            
            #### 🧠 モナド (Monad)
            **文脈保持計算**により、一貫した思考の流れで段階的発展を実現。
            単発の質問応答を超えた、継続的で発展的な知的対話。
            """)
        
        st.markdown("""
        ### 🚀 技術的革新ポイント
        
        - **真の非同期処理**: asyncio による効率的並行実行
        - **プロダクション級堅牢性**: エラーハンドリング・リトライ・フォールバック
        - **インテリジェント最適化**: キャッシュ・バッチ処理・アダプティブ制御
        - **包括的品質保証**: 圏論的性質を含む数学的検証テスト
        
        ### 📊 実装統計
        """)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="performance-metric">', unsafe_allow_html=True)
            st.metric("実装ファイル数", "10+")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="performance-metric">', unsafe_allow_html=True)
            st.metric("テストケース数", "24+")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="performance-metric">', unsafe_allow_html=True)
            st.metric("コード行数", "3000+")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="performance-metric">', unsafe_allow_html=True)
            st.metric("Phase完了", "4/6")
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("""
        ### 🌟 ビジョン
        
        「圏論がAIの標準数学基盤となる未来」を目指し、**数学的厳密性**と**実用的価値**を両立した
        次世代のプロンプトエンジニアリングシステムの研究開発を推進しています。
        
        ### 🔗 関連リンク
        
        - **GitHub**: (設定予定) categorical-prompt-engineering
        - **ドキュメント**: プロジェクト内 .md ファイル群
        - **ライセンス**: MIT License
        
        ---
        
        **Phase 5**: エコシステム構築 実行中 🚧  
        **最終更新**: 2025年8月
        """)
    
    def run(self):
        """アプリ実行"""
        self.render_header()
        self.render_sidebar()
        
        # メインタブ
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "⊗ テンソル積",
            "🔄 自然変換", 
            "🔄 アジョイント関手",
            "🧠 モナド",
            "📖 About"
        ])
        
        with tab1:
            self.render_tensor_product_tab()
        
        with tab2:
            self.render_natural_transformation_tab()
        
        with tab3:
            self.render_adjoint_tab()
        
        with tab4:
            self.render_monad_tab()
        
        with tab5:
            self.render_about_tab()
        
        # フッター
        st.markdown("---")
        st.markdown(
            "<div style='text-align: center; color: #666; font-size: 0.8rem;'>"
            "🧮 圏論的プロンプトエンジニアリング - 数学の美しさと実用的価値の融合<br>"
            "Categorical Prompt Engineering © 2025"
            "</div>",
            unsafe_allow_html=True
        )


def main():
    """メイン関数"""
    ui = StreamlitCategoricalUI()
    ui.run()


if __name__ == "__main__":
    main()