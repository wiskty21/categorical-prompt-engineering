"""
Categorical Prompt Engineering Framework

This module demonstrates how category theory concepts can be applied to prompt engineering,
treating prompts as morphisms between different "cognitive spaces" or contexts.

Key Category Theory Concepts Implemented:
1. Objects: Represent different prompt contexts or domains
2. Morphisms: Functions that transform one context to another (prompts)
3. Composition: Combining prompts in sequence
4. Identity: Neutral prompts that don't change context
5. Associativity: Different ways of composing prompts yield same result
6. Functors: Transformations between different prompt categories
"""

from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, TypeVar, Generic
from dataclasses import dataclass


# Type variables for generic category theory constructs
A = TypeVar('A')
B = TypeVar('B')
C = TypeVar('C')


class CategoryObject:
    """
    Represents an object in our category.
    In prompt engineering, this represents different cognitive contexts or domains.
    
    Examples: "creative_writing", "technical_analysis", "casual_conversation"
    """
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
    
    def __str__(self):
        return f"Object({self.name})"
    
    def __repr__(self):
        return self.__str__()
    
    def __eq__(self, other):
        return isinstance(other, CategoryObject) and self.name == other.name
    
    def __hash__(self):
        return hash(self.name)


class Morphism(Generic[A, B]):
    """
    Represents a morphism (arrow) between two objects in our category.
    In prompt engineering, this is a transformation from one context to another.
    
    A morphism f: A -> B represents a prompt that transforms context A into context B.
    """
    
    def __init__(self, 
                 source: CategoryObject, 
                 target: CategoryObject, 
                 transform: Callable[[str], str],
                 name: str = ""):
        self.source = source
        self.target = target
        self.transform = transform
        self.name = name or f"{source.name} -> {target.name}"
    
    def apply(self, input_text: str) -> str:
        """Apply the morphism transformation to input text"""
        return self.transform(input_text)
    
    def __call__(self, input_text: str) -> str:
        """Make morphism callable"""
        return self.apply(input_text)
    
    def __str__(self):
        return f"Morphism({self.name}: {self.source.name} -> {self.target.name})"
    
    def __repr__(self):
        return self.__str__()


class Category:
    """
    Represents a category with objects and morphisms.
    This is our main prompt engineering framework.
    """
    
    def __init__(self, name: str):
        self.name = name
        self.objects: Dict[str, CategoryObject] = {}
        self.morphisms: List[Morphism] = []
        self._identity_cache: Dict[CategoryObject, Morphism] = {}
    
    def add_object(self, obj: CategoryObject) -> CategoryObject:
        """Add an object to the category"""
        self.objects[obj.name] = obj
        return obj
    
    def add_morphism(self, morphism: Morphism) -> Morphism:
        """Add a morphism to the category"""
        # Ensure source and target objects exist
        if morphism.source.name not in self.objects:
            self.add_object(morphism.source)
        if morphism.target.name not in self.objects:
            self.add_object(morphism.target)
        
        self.morphisms.append(morphism)
        return morphism
    
    def identity(self, obj: CategoryObject) -> Morphism:
        """
        Create identity morphism for an object.
        Identity morphisms leave the input unchanged - they represent neutral prompts.
        """
        if obj not in self._identity_cache:
            def identity_transform(text: str) -> str:
                return text
            
            identity_morphism = Morphism(
                obj, obj, identity_transform, f"id_{obj.name}"
            )
            self._identity_cache[obj] = identity_morphism
        
        return self._identity_cache[obj]
    
    def compose(self, f: Morphism, g: Morphism) -> Morphism:
        """
        Compose two morphisms: (g ∘ f)
        
        For morphisms f: A -> B and g: B -> C,
        composition creates g ∘ f: A -> C
        
        This represents chaining prompts in sequence.
        """
        if f.target != g.source:
            raise ValueError(
                f"Cannot compose {f} and {g}: target of f ({f.target}) "
                f"must equal source of g ({g.source})"
            )
        
        def composed_transform(text: str) -> str:
            # Apply f first, then g
            intermediate = f.apply(text)
            return g.apply(intermediate)
        
        composed_name = f"({g.name} ∘ {f.name})"
        return Morphism(f.source, g.target, composed_transform, composed_name)
    
    def verify_associativity(self, f: Morphism, g: Morphism, h: Morphism, test_input: str = "test") -> bool:
        """
        Verify that composition is associative: (h ∘ g) ∘ f = h ∘ (g ∘ f)
        
        This is a fundamental property of categories and ensures that
        different ways of grouping prompt compositions yield the same result.
        """
        try:
            # Left association: (h ∘ g) ∘ f
            hg = self.compose(g, h)
            left = self.compose(f, hg)
            
            # Right association: h ∘ (g ∘ f)
            gf = self.compose(f, g)
            right = self.compose(gf, h)
            
            # Test with sample input
            left_result = left.apply(test_input)
            right_result = right.apply(test_input)
            
            return left_result == right_result
        except ValueError:
            return False
    
    def get_morphisms_from(self, obj: CategoryObject) -> List[Morphism]:
        """Get all morphisms starting from a given object"""
        return [m for m in self.morphisms if m.source == obj]
    
    def get_morphisms_to(self, obj: CategoryObject) -> List[Morphism]:
        """Get all morphisms ending at a given object"""
        return [m for m in self.morphisms if m.target == obj]


class Functor:
    """
    A functor between two categories.
    
    In prompt engineering, functors allow us to transform entire prompt systems
    from one domain to another while preserving the compositional structure.
    
    For example: translating a prompt system from English to Spanish,
    or adapting prompts from technical to creative domains.
    """
    
    def __init__(self, 
                 name: str,
                 source_category: Category, 
                 target_category: Category,
                 object_map: Callable[[CategoryObject], CategoryObject],
                 morphism_map: Callable[[Morphism], Morphism]):
        self.name = name
        self.source_category = source_category
        self.target_category = target_category
        self.object_map = object_map
        self.morphism_map = morphism_map
    
    def map_object(self, obj: CategoryObject) -> CategoryObject:
        """Map an object from source to target category"""
        return self.object_map(obj)
    
    def map_morphism(self, morphism: Morphism) -> Morphism:
        """Map a morphism from source to target category"""
        return self.morphism_map(morphism)
    
    def verify_composition_preservation(self, f: Morphism, g: Morphism, test_input: str = "test") -> bool:
        """
        Verify that the functor preserves composition:
        F(g ∘ f) = F(g) ∘ F(f)
        
        This ensures that prompt compositions work the same way
        after functor transformation.
        """
        try:
            # Original composition in source category
            composed_original = self.source_category.compose(f, g)
            
            # Map individual morphisms and compose in target category
            f_mapped = self.map_morphism(f)
            g_mapped = self.map_morphism(g)
            composed_mapped = self.target_category.compose(f_mapped, g_mapped)
            
            # Map the composed morphism
            original_mapped = self.map_morphism(composed_original)
            
            # Test equivalence
            result1 = composed_mapped.apply(test_input)
            result2 = original_mapped.apply(test_input)
            
            return result1 == result2
        except ValueError:
            return False


# Practical Prompt Engineering Classes

@dataclass
class PromptTemplate:
    """A template for creating morphisms with common prompt patterns"""
    name: str
    template: str
    input_placeholder: str = "{input}"
    
    def create_morphism(self, source: CategoryObject, target: CategoryObject) -> Morphism:
        """Create a morphism using this template"""
        def transform(text: str) -> str:
            return self.template.format(input=text)
        
        return Morphism(source, target, transform, self.name)


class PromptChain:
    """
    A utility class for building and managing chains of prompts
    using categorical composition.
    """
    
    def __init__(self, category: Category, name: str = ""):
        self.category = category
        self.name = name
        self.chain: List[Morphism] = []
    
    def add(self, morphism: Morphism) -> 'PromptChain':
        """Add a morphism to the chain"""
        if self.chain and self.chain[-1].target != morphism.source:
            raise ValueError(
                f"Cannot add {morphism} to chain: "
                f"previous target {self.chain[-1].target} != current source {morphism.source}"
            )
        self.chain.append(morphism)
        return self
    
    def compose(self) -> Optional[Morphism]:
        """Compose all morphisms in the chain into a single morphism"""
        if not self.chain:
            return None
        
        result = self.chain[0]
        for morphism in self.chain[1:]:
            result = self.category.compose(result, morphism)
        
        return result
    
    def execute(self, input_text: str) -> str:
        """Execute the entire chain on input text"""
        composed = self.compose()
        if composed is None:
            return input_text
        return composed.apply(input_text)


# Example prompt engineering contexts and transformations

def create_basic_prompt_category() -> Category:
    """Create a basic category for prompt engineering with common contexts"""
    
    cat = Category("BasicPrompts")
    
    # Define objects (contexts/domains)
    raw_input = CategoryObject("raw_input", "Raw user input without specific context")
    creative = CategoryObject("creative", "Creative writing context")
    analytical = CategoryObject("analytical", "Analytical thinking context")
    technical = CategoryObject("technical", "Technical documentation context")
    conversational = CategoryObject("conversational", "Friendly conversation context")
    
    # Add objects to category
    cat.add_object(raw_input)
    cat.add_object(creative)
    cat.add_object(analytical)
    cat.add_object(technical)
    cat.add_object(conversational)
    
    # Define morphisms (prompt transformations)
    
    # To creative context
    to_creative = Morphism(
        raw_input, creative,
        lambda text: f"As a creative writer, please expand on this idea: {text}",
        "to_creative"
    )
    
    # To analytical context
    to_analytical = Morphism(
        raw_input, analytical,
        lambda text: f"Please analyze this systematically: {text}",
        "to_analytical"
    )
    
    # To technical context
    to_technical = Morphism(
        raw_input, technical,
        lambda text: f"Provide technical documentation for: {text}",
        "to_technical"
    )
    
    # Creative to conversational
    creative_to_conv = Morphism(
        creative, conversational,
        lambda text: f"Let's discuss this creative idea in a friendly way: {text}",
        "creative_to_conversational"
    )
    
    # Analytical to technical
    analytical_to_tech = Morphism(
        analytical, technical,
        lambda text: f"Based on this analysis, create technical specifications: {text}",
        "analytical_to_technical"
    )
    
    # Add morphisms to category
    cat.add_morphism(to_creative)
    cat.add_morphism(to_analytical)
    cat.add_morphism(to_technical)
    cat.add_morphism(creative_to_conv)
    cat.add_morphism(analytical_to_tech)
    
    return cat


def demonstrate_category_laws():
    """Demonstrate fundamental category theory laws in prompt engineering"""
    
    print("=== Categorical Prompt Engineering Laws ===\n")
    
    cat = create_basic_prompt_category()
    
    # Get some objects and morphisms for testing
    raw_input = cat.objects["raw_input"]
    creative = cat.objects["creative"]
    conversational = cat.objects["conversational"]
    
    to_creative = next(m for m in cat.morphisms if m.name == "to_creative")
    creative_to_conv = next(m for m in cat.morphisms if m.name == "creative_to_conversational")
    
    # Demonstrate identity laws
    print("1. Identity Laws:")
    print("   For any morphism f: A -> B")
    print("   - id_B ∘ f = f")
    print("   - f ∘ id_A = f")
    
    identity_raw = cat.identity(raw_input)
    identity_creative = cat.identity(creative)
    
    # Test left identity: id_creative ∘ to_creative = to_creative
    left_identity = cat.compose(to_creative, identity_creative)
    test_input = "artificial intelligence"
    
    original_result = to_creative.apply(test_input)
    left_identity_result = left_identity.apply(test_input)
    
    print(f"   Original: {original_result}")
    print(f"   Left identity: {left_identity_result}")
    print(f"   Equal: {original_result == left_identity_result}\n")
    
    # Demonstrate associativity
    print("2. Associativity:")
    print("   For morphisms f: A -> B, g: B -> C, h: C -> D")
    print("   (h ∘ g) ∘ f = h ∘ (g ∘ f)")
    
    # We need a third morphism for full associativity test
    # Let's create one: conversational -> raw (summary)
    conv_to_raw = Morphism(
        conversational, raw_input,
        lambda text: f"Summary: {text[:50]}...",
        "summarize"
    )
    cat.add_morphism(conv_to_raw)
    
    is_associative = cat.verify_associativity(to_creative, creative_to_conv, conv_to_raw, test_input)
    print(f"   Associativity verified: {is_associative}\n")


if __name__ == "__main__":
    demonstrate_category_laws()