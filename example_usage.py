"""
Example Usage of Categorical Prompt Engineering Framework

This file demonstrates practical applications of the categorical prompt engineering
framework, showing how to compose prompts, use functors, and build complex
prompt chains using category theory principles.
"""

from categorical_prompt_engineering import (
    Category, CategoryObject, Morphism, Functor, 
    PromptTemplate, PromptChain, create_basic_prompt_category
)


def example_1_basic_composition():
    """Example 1: Basic prompt composition"""
    
    print("=== Example 1: Basic Prompt Composition ===\n")
    
    # Create our category
    cat = create_basic_prompt_category()
    
    # Get some morphisms
    to_creative = next(m for m in cat.morphisms if m.name == "to_creative")
    creative_to_conv = next(m for m in cat.morphisms if m.name == "creative_to_conversational")
    
    # Compose them: raw_input -> creative -> conversational
    composed = cat.compose(to_creative, creative_to_conv)
    
    # Test the composition
    user_input = "machine learning algorithms"
    result = composed.apply(user_input)
    
    print(f"Input: {user_input}")
    print(f"Composed transformation: {result}")
    print()


def example_2_prompt_chains():
    """Example 2: Building complex prompt chains"""
    
    print("=== Example 2: Complex Prompt Chains ===\n")
    
    cat = create_basic_prompt_category()
    
    # Create a complex analysis chain
    chain = PromptChain(cat, "Analysis Chain")
    
    # Get morphisms
    to_analytical = next(m for m in cat.morphisms if m.name == "to_analytical")
    analytical_to_tech = next(m for m in cat.morphisms if m.name == "analytical_to_technical")
    
    # Build the chain
    chain.add(to_analytical).add(analytical_to_tech)
    
    # Execute the chain
    user_input = "blockchain technology"
    result = chain.execute(user_input)
    
    print(f"Input: {user_input}")
    print(f"Chain result: {result}")
    print()


def example_3_custom_morphisms():
    """Example 3: Creating custom morphisms for specific use cases"""
    
    print("=== Example 3: Custom Morphisms ===\n")
    
    # Create a specialized category for code documentation
    doc_cat = Category("DocumentationPrompts")
    
    # Define objects
    code_snippet = CategoryObject("code_snippet", "Raw code input")
    explanation = CategoryObject("explanation", "Code explanation")
    tutorial = CategoryObject("tutorial", "Step-by-step tutorial")
    api_docs = CategoryObject("api_docs", "API documentation")
    
    # Add objects
    doc_cat.add_object(code_snippet)
    doc_cat.add_object(explanation)
    doc_cat.add_object(tutorial)
    doc_cat.add_object(api_docs)
    
    # Create custom morphisms
    explain_code = Morphism(
        code_snippet, explanation,
        lambda code: f"Explain this code step by step:\n\n```\n{code}\n```\n\nExplanation:",
        "explain_code"
    )
    
    create_tutorial = Morphism(
        explanation, tutorial,
        lambda explanation: f"Create a beginner-friendly tutorial based on this explanation:\n\n{explanation}\n\nTutorial:",
        "create_tutorial"
    )
    
    generate_api_docs = Morphism(
        code_snippet, api_docs,
        lambda code: f"Generate API documentation for this code:\n\n```\n{code}\n```\n\nAPI Documentation:",
        "generate_api_docs"
    )
    
    # Add morphisms
    doc_cat.add_morphism(explain_code)
    doc_cat.add_morphism(create_tutorial)
    doc_cat.add_morphism(generate_api_docs)
    
    # Test the custom morphisms
    sample_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
"""
    
    # Direct transformation to API docs
    api_result = generate_api_docs.apply(sample_code)
    print("Direct to API docs:")
    print(api_result)
    print()
    
    # Composed transformation: code -> explanation -> tutorial
    explanation_result = explain_code.apply(sample_code)
    tutorial_result = create_tutorial.apply(explanation_result)
    
    print("Composed: Code -> Explanation -> Tutorial:")
    print(tutorial_result)
    print()


def example_4_functors():
    """Example 4: Using functors to transform between categories"""
    
    print("=== Example 4: Functors - Domain Translation ===\n")
    
    # Create source category (technical)
    tech_cat = create_basic_prompt_category()
    
    # Create target category (educational)
    edu_cat = Category("EducationalPrompts")
    
    # Define educational objects
    student_input = CategoryObject("student_input", "Student question or topic")
    beginner_friendly = CategoryObject("beginner_friendly", "Beginner-friendly explanation")
    interactive = CategoryObject("interactive", "Interactive learning content")
    
    edu_cat.add_object(student_input)
    edu_cat.add_object(beginner_friendly)
    edu_cat.add_object(interactive)
    
    # Create functor to translate technical prompts to educational ones
    def object_translator(obj: CategoryObject) -> CategoryObject:
        """Translate technical objects to educational equivalents"""
        mapping = {
            "raw_input": student_input,
            "technical": beginner_friendly,
            "analytical": interactive
        }
        return mapping.get(obj.name, obj)
    
    def morphism_translator(morphism: Morphism) -> Morphism:
        """Translate technical morphisms to educational equivalents"""
        source_mapped = object_translator(morphism.source)
        target_mapped = object_translator(morphism.target)
        
        def educational_transform(text: str) -> str:
            # Apply original transformation but with educational framing
            original_result = morphism.apply(text)
            return f"For a beginner learning this topic: {original_result}"
        
        return Morphism(
            source_mapped, target_mapped, 
            educational_transform, 
            f"edu_{morphism.name}"
        )
    
    # Create the functor
    tech_to_edu_functor = Functor(
        "TechnicalToEducational",
        tech_cat, edu_cat,
        object_translator,
        morphism_translator
    )
    
    # Test the functor
    to_technical = next(m for m in tech_cat.morphisms if m.name == "to_technical")
    edu_morphism = tech_to_edu_functor.map_morphism(to_technical)
    
    test_input = "neural networks"
    original_result = to_technical.apply(test_input)
    educational_result = edu_morphism.apply(test_input)
    
    print(f"Input: {test_input}")
    print(f"Technical result: {original_result}")
    print(f"Educational result: {educational_result}")
    print()


def example_5_prompt_templates():
    """Example 5: Using prompt templates for reusable patterns"""
    
    print("=== Example 5: Prompt Templates ===\n")
    
    cat = Category("TemplateCategory")
    
    # Define objects
    question = CategoryObject("question", "User question")
    analysis = CategoryObject("analysis", "Analytical response")
    summary = CategoryObject("summary", "Concise summary")
    
    cat.add_object(question)
    cat.add_object(analysis)
    cat.add_object(summary)
    
    # Create reusable prompt templates
    analysis_template = PromptTemplate(
        "deep_analysis",
        "Provide a comprehensive analysis of the following topic:\n\nTopic: {input}\n\nAnalysis:\n1. Overview\n2. Key Components\n3. Implications\n4. Conclusion"
    )
    
    summary_template = PromptTemplate(
        "executive_summary",
        "Create an executive summary of the following analysis:\n\n{input}\n\nExecutive Summary:"
    )
    
    # Create morphisms using templates
    analyze = analysis_template.create_morphism(question, analysis)
    summarize = summary_template.create_morphism(analysis, summary)
    
    cat.add_morphism(analyze)
    cat.add_morphism(summarize)
    
    # Test the template-based morphisms
    user_question = "What are the implications of quantum computing?"
    
    analysis_result = analyze.apply(user_question)
    summary_result = summarize.apply(analysis_result)
    
    print(f"Question: {user_question}")
    print(f"\nAnalysis: {analysis_result}")
    print(f"\nSummary: {summary_result}")
    print()


def example_6_associativity_in_practice():
    """Example 6: Demonstrating associativity in practical prompt engineering"""
    
    print("=== Example 6: Associativity in Practice ===\n")
    
    cat = Category("ContentCreation")
    
    # Define content creation pipeline objects
    raw_idea = CategoryObject("raw_idea", "Initial content idea")
    outline = CategoryObject("outline", "Structured outline")
    draft = CategoryObject("draft", "First draft")
    polished = CategoryObject("polished", "Polished content")
    
    # Add objects
    for obj in [raw_idea, outline, draft, polished]:
        cat.add_object(obj)
    
    # Create morphisms for content creation pipeline
    create_outline = Morphism(
        raw_idea, outline,
        lambda idea: f"Content Outline for: {idea}\n1. Introduction\n2. Main Points\n3. Conclusion",
        "create_outline"
    )
    
    write_draft = Morphism(
        outline, draft,
        lambda outline: f"Draft based on outline:\n{outline}\n\n[Draft content would be generated here]",
        "write_draft"
    )
    
    polish_content = Morphism(
        draft, polished,
        lambda draft: f"Polished version:\n{draft}\n\n[Enhanced with better flow and style]",
        "polish_content"
    )
    
    # Add morphisms
    cat.add_morphism(create_outline)
    cat.add_morphism(write_draft)
    cat.add_morphism(polish_content)
    
    # Demonstrate associativity: (polish ∘ write) ∘ outline = polish ∘ (write ∘ outline)
    test_idea = "The future of sustainable energy"
    
    # Method 1: Left association
    write_then_polish = cat.compose(write_draft, polish_content)
    left_composition = cat.compose(create_outline, write_then_polish)
    
    # Method 2: Right association  
    outline_then_write = cat.compose(create_outline, write_draft)
    right_composition = cat.compose(outline_then_write, polish_content)
    
    # Both should produce equivalent results
    left_result = left_composition.apply(test_idea)
    right_result = right_composition.apply(test_idea)
    
    print(f"Content idea: {test_idea}")
    print(f"\nLeft association result: {left_result}")
    print(f"\nRight association result: {right_result}")
    print(f"\nResults are equivalent: {left_result == right_result}")
    
    # Verify using the category's built-in method
    is_associative = cat.verify_associativity(create_outline, write_draft, polish_content, test_idea)
    print(f"Associativity verified: {is_associative}")
    print()


def main():
    """Run all examples to demonstrate the categorical prompt engineering framework"""
    
    print("Categorical Prompt Engineering - Example Usage")
    print("=" * 50)
    print()
    
    # Run all examples
    example_1_basic_composition()
    example_2_prompt_chains()
    example_3_custom_morphisms()
    example_4_functors()
    example_5_prompt_templates()
    example_6_associativity_in_practice()
    
    print("All examples completed!")
    print("\nKey takeaways:")
    print("1. Prompts can be treated as morphisms between cognitive contexts")
    print("2. Composition allows building complex prompt chains from simple parts")
    print("3. Category theory laws ensure predictable behavior")
    print("4. Functors enable translation between different prompt domains")
    print("5. Templates provide reusable prompt patterns")
    print("6. Associativity guarantees consistent results regardless of grouping")


if __name__ == "__main__":
    main()