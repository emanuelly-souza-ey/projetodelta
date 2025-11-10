"""
Manual test script for router agent classification.
Tests if the router correctly distinguishes between project_search and project_selection.
"""

import asyncio
from backend.agents.router_agent import RouterAgent


def test_classification():
    """Test router classification with example queries."""
    
    router = RouterAgent(session_id="test_classification")
    
    # Test cases: (query, expected_intent)
    test_cases = [
        # Project Search cases (exploratory)
        ("Mostrar projetos de IA", "project_search"),
        ("Quais projetos temos disponíveis?", "project_search"),
        ("Listar projetos ativos", "project_search"),
        ("Buscar projetos com Python", "project_search"),
        ("Encontrar projetos de Machine Learning", "project_search"),
        
        # Project Selection cases (specific action)
        ("Selecionar projeto Delta", "project_selection"),
        ("Quero trabalhar no GenAI", "project_selection"),
        ("Escolher projeto X", "project_selection"),
        ("Mudar para projeto Y", "project_selection"),
        ("Usar projeto Delta Platform", "project_selection"),
        ("2", "project_selection"),  # Number after listing
        
        # Other intents
        ("Quantas horas trabalhei hoje?", "worked_hours"),
        ("Como está o progresso do projeto?", "project_progress"),
    ]
    
    print("\n" + "="*80)
    print("ROUTER CLASSIFICATION TEST")
    print("="*80 + "\n")
    
    correct = 0
    total = len(test_cases)
    
    for query, expected in test_cases:
        intent = router.classify_intent(query, conversation_id=None)
        
        is_correct = intent.category == expected
        status = "✅ PASS" if is_correct else "❌ FAIL"
        
        if is_correct:
            correct += 1
        
        print(f"{status} | Query: '{query}'")
        print(f"       Expected: {expected}")
        print(f"       Got: {intent.category} (confidence: {intent.confidence:.2f})")
        print(f"       Reasoning: {intent.reasoning}")
        print()
    
    print("="*80)
    print(f"RESULTS: {correct}/{total} correct ({(correct/total)*100:.1f}%)")
    print("="*80)
    
    return correct >= (total * 0.9)  # 90% accuracy threshold


if __name__ == "__main__":
    success = test_classification()
    exit(0 if success else 1)
