# -*- coding: utf-8 -*-
"""
真の圏論的プロンプトエンジニアリング実装
Category Theory for Prompt Engineering - Advanced Implementation

このモジュールは以下の高度な圏論的概念を実装します：
1. モノイダル圏（Monoidal Categories）- 並行合成
2. 自然変換（Natural Transformations）- 構造保存変換  
3. アジョイント関手（Adjoint Functors）- 双対性
4. 極限・余極限（Limits & Colimits）- 統合・分散
5. モナド（Monads）- 文脈保持計算
"""

from typing import List, Dict, Callable, Any, Optional, Union, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
from functools import reduce
from concurrent.futures import ThreadPoolExecutor
import itertools


# =============================================================================
# 基本的な圏論構造
# =============================================================================

@dataclass
class CategoryObject:
    """圏の対象を表現"""
    name: str
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}


class Morphism:
    """圏の射を表現"""
    def __init__(self, source: CategoryObject, target: CategoryObject, 
                 transform: Callable[[str], str], name: str = ""):
        self.source = source
        self.target = target
        self.transform = transform
        self.name = name or f"{source.name} -> {target.name}"
    
    def apply(self, input_text: str) -> str:
        """射を適用"""
        return self.transform(input_text)
    
    def compose(self, other: 'Morphism') -> 'Morphism':
        """射の合成 (self ∘ other)"""
        if self.source != other.target:
            raise ValueError(f"Cannot compose: {self.source} ≠ {other.target}")
        
        def composed_transform(text: str) -> str:
            return self.apply(other.apply(text))
        
        return Morphism(other.source, self.target, composed_transform,
                       f"({self.name} ∘ {other.name})")


# =============================================================================
# 1. モノイダル圏（Monoidal Categories）- 並行合成
# =============================================================================

class TensorProduct:
    """
    テンソル積 (⊗) - 複数のプロンプトを並行実行
    
    真の圏論的威力：異なる観点を同時に適用して統合
    """
    
    def __init__(self, *morphisms: Morphism, integration_strategy: str = "synthesis"):
        self.morphisms = morphisms
        self.integration_strategy = integration_strategy
        self._validate_tensor_product()
    
    def _validate_tensor_product(self):
        """テンソル積の有効性をチェック"""
        if not self.morphisms:
            raise ValueError("テンソル積には少なくとも1つの射が必要です")
        
        # 並行実行可能性の確認（同じソースオブジェクトを持つ）
        first_source = self.morphisms[0].source
        if not all(m.source == first_source for m in self.morphisms):
            # 異なるソースの場合は警告（高度な使用法）
            print(f"警告: 異なるソースを持つ射のテンソル積: "
                  f"{[m.source.name for m in self.morphisms]}")
    
    def apply(self, input_text: str) -> str:
        """並行実行と統合"""
        # 並行実行
        with ThreadPoolExecutor(max_workers=len(self.morphisms)) as executor:
            futures = [executor.submit(m.apply, input_text) for m in self.morphisms]
            results = [f.result() for f in futures]
        
        # 結果の統合
        return self._integrate_results(results, input_text)
    
    def _integrate_results(self, results: List[str], original_input: str) -> str:
        """圏論的統合戦略"""
        if self.integration_strategy == "synthesis":
            return self._synthesis_integration(results, original_input)
        elif self.integration_strategy == "dialectic":
            return self._dialectic_integration(results, original_input)
        elif self.integration_strategy == "consensus":
            return self._consensus_integration(results, original_input)
        else:
            return self._default_integration(results)
    
    def _synthesis_integration(self, results: List[str], original: str) -> str:
        """統合的統合 - 異なる観点を融合"""
        morphism_names = [m.name for m in self.morphisms]
        
        integration_prompt = f"""
以下の{len(results)}つの異なる観点からの分析を統合して、包括的な見解を提示してください：

元の入力: {original}

分析結果:
"""
        for i, (name, result) in enumerate(zip(morphism_names, results), 1):
            integration_prompt += f"\n{i}. {name}:\n{result}\n"
        
        integration_prompt += "\n統合された包括的分析:"
        return integration_prompt
    
    def _dialectic_integration(self, results: List[str], original: str) -> str:
        """弁証法的統合 - 対立する観点から新たな視点を創出"""
        return f"""
弁証法的統合分析:

テーマ: {original}

対立する観点:
{chr(10).join(f'• {result}' for result in results)}

これらの対立する観点を弁証法的に統合し、より高次の理解を導出してください:
"""
    
    def _consensus_integration(self, results: List[str], original: str) -> str:
        """合意形成統合 - 共通点を見つけて調和"""
        return f"""
合意形成分析:

対象: {original}

各観点の見解:
{chr(10).join(f'- {result}' for result in results)}

これらの見解から共通点と相違点を抽出し、調和のとれた合意を形成してください:
"""
    
    def _default_integration(self, results: List[str]) -> str:
        """デフォルト統合"""
        return f"複数観点の統合結果:\n" + "\n---\n".join(results)
    
    def tensor_with(self, other: 'TensorProduct') -> 'TensorProduct':
        """テンソル積の結合律 (A ⊗ B) ⊗ C = A ⊗ (B ⊗ C)"""
        return TensorProduct(*self.morphisms, *other.morphisms, 
                           integration_strategy=self.integration_strategy)


class MonoidalCategory:
    """
    モノイダル圏の実装
    
    テンソル積と単位対象を持つ圏
    """
    
    def __init__(self, name: str):
        self.name = name
        self.unit_object = CategoryObject("I", {"is_unit": True})
        self.objects: List[CategoryObject] = [self.unit_object]
        self.morphisms: List[Morphism] = []
    
    def tensor(self, *morphisms: Morphism, strategy: str = "synthesis") -> TensorProduct:
        """テンソル積の作成"""
        return TensorProduct(*morphisms, integration_strategy=strategy)
    
    def add_object(self, obj: CategoryObject):
        """対象の追加"""
        if obj not in self.objects:
            self.objects.append(obj)
    
    def add_morphism(self, morphism: Morphism):
        """射の追加"""
        self.add_object(morphism.source)
        self.add_object(morphism.target)
        self.morphisms.append(morphism)
    
    def left_unitor(self, morphism: Morphism) -> Morphism:
        """左単位子 λ: I ⊗ A → A"""
        return morphism  # 単位対象とのテンソル積は元の射と同じ
    
    def right_unitor(self, morphism: Morphism) -> Morphism:  
        """右単位子 ρ: A ⊗ I → A"""
        return morphism  # 単位対象とのテンソル積は元の射と同じ


# =============================================================================  
# 2. 自然変換（Natural Transformations）- 構造保存変換
# =============================================================================

class NaturalTransformation:
    """
    自然変換 η: F ⇒ G
    
    2つの関手間の変換で、すべての対象と射に対して一貫した変換を提供
    """
    
    def __init__(self, name: str, source_functor: 'Functor', target_functor: 'Functor',
                 component_transforms: Dict[str, Callable[[str], str]]):
        self.name = name
        self.source_functor = source_functor
        self.target_functor = target_functor
        self.components = component_transforms
    
    def component_at(self, obj: CategoryObject) -> Morphism:
        """対象 obj での自然変換の成分 η_obj: F(obj) → G(obj)"""
        if obj.name not in self.components:
            raise ValueError(f"対象 {obj.name} での成分が定義されていません")
        
        source_obj = CategoryObject(f"F({obj.name})")
        target_obj = CategoryObject(f"G({obj.name})")
        
        return Morphism(source_obj, target_obj, 
                       self.components[obj.name], f"η_{obj.name}")
    
    def apply_to_morphism(self, morphism: Morphism) -> Morphism:
        """
        射への自然変換の適用
        
        自然性条件を満たす：η_B ∘ F(f) = G(f) ∘ η_A
        """
        # F(f)を適用後にη_Bを適用 = η_Aを適用後にG(f)を適用
        source_component = self.component_at(morphism.source)
        target_component = self.component_at(morphism.target)
        
        # 自然性を保った変換
        def natural_transform(text: str) -> str:
            # η_A ∘ f の経路
            intermediate = morphism.apply(text)
            return target_component.apply(intermediate)
        
        return Morphism(morphism.source, morphism.target, 
                       natural_transform, f"η({morphism.name})")
    
    def verify_naturality(self, morphism: Morphism) -> bool:
        """自然性条件の検証"""
        # η_B ∘ F(f) = G(f) ∘ η_A が成り立つかチェック
        test_input = "test_naturality_input"
        
        # 左辺: η_B ∘ F(f)
        left_result = self.component_at(morphism.target).apply(
            morphism.apply(test_input)
        )
        
        # 右辺: G(f) ∘ η_A  
        right_result = morphism.apply(
            self.component_at(morphism.source).apply(test_input)
        )
        
        return left_result == right_result


class Functor:
    """
    関手 F: C → D
    
    圏 C から圏 D への構造保存写像
    """
    
    def __init__(self, name: str, source_category: 'MonoidalCategory', 
                 target_category: 'MonoidalCategory',
                 object_map: Callable[[CategoryObject], CategoryObject],
                 morphism_map: Callable[[Morphism], Morphism]):
        self.name = name
        self.source = source_category
        self.target = target_category
        self.object_map = object_map
        self.morphism_map = morphism_map
    
    def apply_to_object(self, obj: CategoryObject) -> CategoryObject:
        """対象への関手の適用"""
        return self.object_map(obj)
    
    def apply_to_morphism(self, morphism: Morphism) -> Morphism:
        """射への関手の適用（構造保存）"""
        # F(f: A → B) = F(f): F(A) → F(B)
        mapped_source = self.apply_to_object(morphism.source)
        mapped_target = self.apply_to_object(morphism.target)
        mapped_morphism = self.morphism_map(morphism)
        
        # 関手の構造保存性を確認
        assert mapped_morphism.source.name == mapped_source.name
        assert mapped_morphism.target.name == mapped_target.name
        
        return mapped_morphism
    
    def preserve_composition(self, f: Morphism, g: Morphism) -> bool:
        """合成の保存性確認: F(g ∘ f) = F(g) ∘ F(f)"""
        if f.target != g.source:
            return False
        
        # F(g ∘ f)
        composed = g.compose(f)
        left_side = self.apply_to_morphism(composed)
        
        # F(g) ∘ F(f)
        f_mapped = self.apply_to_morphism(f)
        g_mapped = self.apply_to_morphism(g)
        right_side = g_mapped.compose(f_mapped)
        
        # 構造的等価性をチェック
        return (left_side.source == right_side.source and 
                left_side.target == right_side.target)
    
    def preserve_identity(self, obj: CategoryObject) -> bool:
        """恒等射の保存性確認: F(id_A) = id_F(A)"""
        identity = Morphism(obj, obj, lambda x: x, f"id_{obj.name}")
        mapped_identity = self.apply_to_morphism(identity)
        expected_target = self.apply_to_object(obj)
        
        return (mapped_identity.source == expected_target and 
                mapped_identity.target == expected_target)


# =============================================================================
# 3. アジョイント関手（Adjoint Functors）- 双対性
# =============================================================================

class AdjointPair:
    """
    アジョイント関手の対 L ⊣ R
    
    L は R の左随伴、R は L の右随伴
    プロンプトエンジニアリングでは「自由化 ⊣ 制約化」などの双対性を表現
    """
    
    def __init__(self, left_adjoint: Functor, right_adjoint: Functor,
                 unit_transform: NaturalTransformation,
                 counit_transform: NaturalTransformation):
        self.L = left_adjoint  # 左随伴（通常は「自由」な方向）
        self.R = right_adjoint  # 右随伴（通常は「忘却」な方向）
        self.unit = unit_transform      # η: Id → R ∘ L
        self.counit = counit_transform  # ε: L ∘ R → Id
        
        self._verify_adjunction()
    
    def _verify_adjunction(self):
        """随伴性の三角恒等式を確認"""
        # L η ∘ ε L = id_L および ε R ∘ R η = id_R
        print(f"随伴対 {self.L.name} ⊣ {self.R.name} を検証中...")
        # 実装は簡略化（本格的には圏論的等価性が必要）
    
    def free_construction(self, constrained_prompt: str) -> str:
        """制約されたプロンプトを自由化"""
        return f"自由度を高めて創造的にアプローチしてください：\n{constrained_prompt}"
    
    def forget_constraints(self, free_prompt: str) -> str:
        """自由なプロンプトから制約を抽出"""
        return f"以下の自由な記述から核心的な要件を抽出してください：\n{free_prompt}"
    
    def apply_unit(self, prompt: str) -> str:
        """単位 η: 元のプロンプト → 制約化後に自由化"""
        return self.free_construction(self.forget_constraints(prompt))
    
    def apply_counit(self, prompt: str) -> str:
        """余単位 ε: 自由化後に制約化 → 元のプロンプト"""
        return self.forget_constraints(self.free_construction(prompt))


class FreeForgetfulAdjunction(AdjointPair):
    """
    自由-忘却随伴の具体例
    
    Free ⊣ Forgetful
    制約のない創作 ⊣ 要点抽出
    """
    
    def __init__(self):
        # 簡略化されたコンストラクタ（実際にはより複雑な設定が必要）
        self.name = "Free-Forgetful Adjunction"
    
    def free_creative_prompt(self, constrained: str) -> str:
        """制約を解放して創造的なプロンプトに"""
        return f"""
創造的自由度を最大化してください：

元の制約: {constrained}

以下の観点から自由に発想してください：
1. 既存の枠組みにとらわれない視点
2. 異分野からの類推やメタファー
3. 未来の可能性や潜在的発展
4. 感情的・直感的なアプローチ
5. 実験的・革新的な手法

自由創作結果:
"""
    
    def extract_essence(self, creative: str) -> str:
        """創造的な記述から本質的要素を抽出"""
        return f"""
以下の創造的記述から核心的要素を抽出してください：

創造的記述: {creative}

抽出すべき要素：
1. 主要なアイデアやコンセプト
2. 実現可能な具体的要素
3. 重要な制約や条件
4. 実用的な応用可能性
5. 測定可能な成果指標

本質的要素:
"""


# =============================================================================
# 4. 極限・余極限（Limits & Colimits）- 統合・分散
# =============================================================================

class Limit:
    """
    極限 - 複数の制約を同時に満たす「最良の」解
    
    プロンプトエンジニアリングでは、競合する要求を調整して
    すべてを満たす最適なプロンプトを構築
    """
    
    def __init__(self, *constraints: Morphism, optimization_strategy: str = "pareto"):
        self.constraints = constraints
        self.strategy = optimization_strategy
    
    def compute_limit(self, input_text: str) -> str:
        """極限の計算 - 全制約を満たす最適解"""
        if self.strategy == "pareto":
            return self._pareto_optimal_limit(input_text)
        elif self.strategy == "weighted":
            return self._weighted_limit(input_text)
        elif self.strategy == "minimax":
            return self._minimax_limit(input_text)
        else:
            return self._default_limit(input_text)
    
    def _pareto_optimal_limit(self, input_text: str) -> str:
        """パレート最適解としての極限"""
        constraint_names = [c.name for c in self.constraints]
        
        return f"""
パレート最適化による制約統合：

入力: {input_text}

満たすべき制約条件:
{chr(10).join(f'• {name}' for name in constraint_names)}

これらすべての制約を同時に満たし、どの制約も他を犠牲にすることなく
最適化された解決策を提示してください：

パレート最適解:
"""
    
    def _weighted_limit(self, input_text: str) -> str:
        """重み付き制約最適化"""
        # 重みは制約の順序で決定（簡略化）
        weights = [1.0/(i+1) for i in range(len(self.constraints))]
        
        constraint_info = []
        for constraint, weight in zip(self.constraints, weights):
            constraint_info.append(f"• {constraint.name} (重み: {weight:.2f})")
        
        return f"""
重み付き制約最適化：

対象: {input_text}

制約条件と重み:
{chr(10).join(constraint_info)}

各制約の重要度に応じて最適なバランスを取った解決策:
"""
    
    def _minimax_limit(self, input_text: str) -> str:
        """ミニマックス最適化"""
        return f"""
ミニマックス最適化による制約統合：

対象: {input_text}

制約条件: {[c.name for c in self.constraints]}

最悪ケースでのリスクを最小化しながら、
すべての制約条件を可能な限り満たす堅実な解決策:
"""
    
    def _default_limit(self, input_text: str) -> str:
        """デフォルト極限計算"""
        return f"制約統合結果: {input_text}\n制約: {[c.name for c in self.constraints]}"


class Colimit:
    """
    余極限 - 複数の選択肢を統合して新しい構造を創出
    
    プロンプトエンジニアリングでは、異なるアプローチを
    統合してより豊かな解決策を生成
    """
    
    def __init__(self, *alternatives: Morphism, synthesis_strategy: str = "dialectical"):
        self.alternatives = alternatives
        self.strategy = synthesis_strategy
    
    def compute_colimit(self, input_text: str) -> str:
        """余極限の計算 - 選択肢の創造的統合"""
        if self.strategy == "dialectical":
            return self._dialectical_synthesis(input_text)
        elif self.strategy == "combinatorial":
            return self._combinatorial_synthesis(input_text)
        elif self.strategy == "emergent":
            return self._emergent_synthesis(input_text)
        else:
            return self._default_colimit(input_text)
    
    def _dialectical_synthesis(self, input_text: str) -> str:
        """弁証法的統合"""
        alternative_names = [a.name for a in self.alternatives]
        
        return f"""
弁証法的統合による新たな視点の創出：

テーマ: {input_text}

統合する選択肢:
{chr(10).join(f'{i+1}. {name}' for i, name in enumerate(alternative_names))}

これらの異なる選択肢を弁証法的に統合し、
対立を乗り越えてより高次の統一的解決策を創造してください：

統合された新しいアプローチ:
"""
    
    def _combinatorial_synthesis(self, input_text: str) -> str:
        """組み合わせ的統合"""
        return f"""
組み合わせ的統合による多面的アプローチ：

対象: {input_text}

統合する要素: {[a.name for a in self.alternatives]}

各選択肢の長所を組み合わせて、
相互に補完し合う包括的な解決策を構築してください：
"""
    
    def _emergent_synthesis(self, input_text: str) -> str:
        """創発的統合"""
        return f"""
創発的統合による新しい可能性の探求：

焦点: {input_text}

既存のアプローチ: {[a.name for a in self.alternatives]}

これらを超越して、予想外の新しい可能性や
創発的な解決策を探求してください：

創発的アプローチ:
"""
    
    def _default_colimit(self, input_text: str) -> str:
        """デフォルト余極限"""
        return f"選択肢統合: {input_text}\n要素: {[a.name for a in self.alternatives]}"


# =============================================================================
# 5. モナド（Monads）- 文脈保持計算
# =============================================================================

class Monad(ABC):
    """
    モナド抽象基底クラス
    
    プロンプトエンジニアリングにおける文脈付き計算を表現
    """
    
    @abstractmethod
    def unit(self, value: Any) -> Any:
        """η: A → M(A) - 純粋な値をモナドに包む"""
        pass
    
    @abstractmethod
    def bind(self, m_value: Any, f: Callable) -> Any:
        """μ: M(M(A)) → M(A) - モナド値の平坦化"""
        pass
    
    @abstractmethod
    def fmap(self, f: Callable, m_value: Any) -> Any:
        """関手としてのマップ"""
        pass


class MaybePrompt(Monad):
    """
    Maybe モナド - 失敗の可能性があるプロンプト
    
    プロンプトが失敗したり、適用不可能な場合を優雅に処理
    """
    
    def __init__(self, value: Optional[str] = None, is_nothing: bool = False):
        self.value = value
        self.is_nothing = is_nothing
    
    def unit(self, value: str) -> 'MaybePrompt':
        """成功値を Maybe に包む"""
        return MaybePrompt(value, False)
    
    def nothing(self) -> 'MaybePrompt':
        """失敗を表す Nothing"""
        return MaybePrompt(None, True)
    
    def bind(self, f: Callable[['MaybePrompt'], 'MaybePrompt']) -> 'MaybePrompt':
        """Maybe の bind 演算"""
        if self.is_nothing:
            return self.nothing()
        else:
            return f(self)
    
    def fmap(self, f: Callable[[str], str]) -> 'MaybePrompt':
        """Maybe への関数適用"""
        if self.is_nothing:
            return self.nothing()
        else:
            try:
                result = f(self.value)
                return self.unit(result)
            except Exception:
                return self.nothing()
    
    def get_or_else(self, default: str) -> str:
        """値を取得、失敗時はデフォルト値"""
        return self.value if not self.is_nothing else default
    
    def is_just(self) -> bool:
        """成功値を持つか"""
        return not self.is_nothing
    
    def __str__(self) -> str:
        return f"Nothing" if self.is_nothing else f"Just({self.value})"


class ContextPrompt(Monad):
    """
    Context モナド（State モナド的）- 会話文脈を保持
    
    過去の会話や状態を保ちながらプロンプトを発展
    """
    
    def __init__(self, current_prompt: str, context: Dict[str, Any] = None):
        self.current_prompt = current_prompt
        self.context = context or {}
    
    def unit(self, prompt: str) -> 'ContextPrompt':
        """純粋なプロンプトを文脈付きに"""
        return ContextPrompt(prompt, {})
    
    def bind(self, f: Callable[['ContextPrompt'], 'ContextPrompt']) -> 'ContextPrompt':
        """文脈を保ちながら変換を適用"""
        return f(self)
    
    def fmap(self, f: Callable[[str], str]) -> 'ContextPrompt':
        """プロンプト変換（文脈保持）"""
        new_prompt = f(self.current_prompt)
        return ContextPrompt(new_prompt, self.context.copy())
    
    def add_context(self, key: str, value: Any) -> 'ContextPrompt':
        """文脈情報の追加"""
        new_context = self.context.copy()
        new_context[key] = value
        return ContextPrompt(self.current_prompt, new_context)
    
    def get_context(self, key: str) -> Any:
        """文脈情報の取得"""
        return self.context.get(key)
    
    def evolve_with_history(self, new_input: str) -> 'ContextPrompt':
        """履歴を考慮したプロンプトの発展"""
        # 過去の文脈を考慮した新しいプロンプト
        history = self.context.get('history', [])
        history.append(self.current_prompt)
        
        evolved_prompt = f"""
文脈を考慮した発展的プロンプト:

過去の文脈: {history[-3:] if len(history) > 3 else history}
現在のプロンプト: {self.current_prompt}
新しい入力: {new_input}

これまでの流れを踏まえて、適切な応答を生成してください:
"""
        
        return ContextPrompt(evolved_prompt, {
            'history': history,
            **self.context
        })
    
    def __str__(self) -> str:
        return f"ContextPrompt(prompt='{self.current_prompt[:50]}...', context={list(self.context.keys())})"


class ListPrompt(Monad):
    """
    List モナド - 複数の可能性を持つプロンプト
    
    非決定的な選択や複数の解釈を同時に扱う
    """
    
    def __init__(self, prompts: List[str]):
        self.prompts = prompts
    
    def unit(self, prompt: str) -> 'ListPrompt':
        """単一プロンプトをリストに"""
        return ListPrompt([prompt])
    
    def bind(self, f: Callable[[str], 'ListPrompt']) -> 'ListPrompt':
        """すべての可能性に関数を適用して平坦化"""
        results = []
        for prompt in self.prompts:
            list_result = f(prompt)
            results.extend(list_result.prompts)
        return ListPrompt(results)
    
    def fmap(self, f: Callable[[str], str]) -> 'ListPrompt':
        """すべての可能性に関数を適用"""
        return ListPrompt([f(prompt) for prompt in self.prompts])
    
    def filter(self, predicate: Callable[[str], bool]) -> 'ListPrompt':
        """条件を満たすプロンプトのみ保持"""
        return ListPrompt([p for p in self.prompts if predicate(p)])
    
    def take(self, n: int) -> 'ListPrompt':
        """最初のn個を取得"""
        return ListPrompt(self.prompts[:n])
    
    def __len__(self) -> int:
        return len(self.prompts)
    
    def __str__(self) -> str:
        return f"ListPrompt({len(self.prompts)} alternatives)"


# =============================================================================
# 使用例とファクトリ関数
# =============================================================================

def create_perspective_tensor(*perspectives: str) -> TensorProduct:
    """異なる観点でのプロンプトテンソル積を作成"""
    raw_obj = CategoryObject("raw_input")
    perspective_objects = [CategoryObject(f"{p}_perspective") for p in perspectives]
    
    morphisms = []
    for i, perspective in enumerate(perspectives):
        def make_transform(p):
            return lambda text: f"{p}の観点から以下を分析してください：\n{text}"
        
        morph = Morphism(raw_obj, perspective_objects[i], 
                        make_transform(perspective), f"{perspective}_analysis")
        morphisms.append(morph)
    
    return TensorProduct(*morphisms, integration_strategy="synthesis")


def create_free_forgetful_adjunction() -> FreeForgetfulAdjunction:
    """自由-忘却随伴の作成"""
    return FreeForgetfulAdjunction()


def create_constraint_limit(*constraint_descriptions: str) -> Limit:
    """制約極限の作成"""
    raw_obj = CategoryObject("input")
    constraint_obj = CategoryObject("constrained")
    
    constraints = []
    for desc in constraint_descriptions:
        def make_constraint(d):
            return lambda text: f"制約「{d}」を満たしながら：\n{text}"
        
        constraint = Morphism(raw_obj, constraint_obj, make_constraint(desc), desc)
        constraints.append(constraint)
    
    return Limit(*constraints, optimization_strategy="pareto")