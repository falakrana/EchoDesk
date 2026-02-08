"""
Test script for LLM-based Natural Language Interpreter

This script demonstrates the LLM integration with Groq.
It tests various natural language inputs and shows how the LLM
interprets them into structured goals.
"""

import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm.interpreter import NaturalLanguageInterpreter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_interpreter():
    """Test the LLM interpreter with various inputs."""
    
    print("\n" + "=" * 80)
    print("LLM INTERPRETER TEST - Groq Integration")
    print("=" * 80)
    
    # Initialize interpreter with LLM enabled
    print("\n[1] Initializing LLM interpreter...")
    interpreter_llm = NaturalLanguageInterpreter(use_llm=True)
    
    # Initialize rule-based interpreter for comparison
    print("[2] Initializing rule-based interpreter...")
    interpreter_rules = NaturalLanguageInterpreter(use_llm=False)
    
    # Test cases
    test_inputs = [
        # Specific app mentions
        "I want to use brave",
        "open chrome please",
        "launch notepad",
        "start visual studio code",
        
        # General intents
        "I need to browse the web",
        "I want to write some notes",
        "open a text editor",
        "I need to check my email",
        
        # Ambiguous inputs
        "help me with something",
        "what can you do",
        
        # Multi-word app names
        "open microsoft edge",
        "launch google chrome",
        
        # Casual language
        "yo open brave for me",
        "can u start notepad",
        "i wanna use firefox",
    ]
    
    print("\n" + "=" * 80)
    print("TESTING VARIOUS INPUTS")
    print("=" * 80)
    
    for i, user_input in enumerate(test_inputs, 1):
        print(f"\n{'─' * 80}")
        print(f"Test {i}/{len(test_inputs)}: \"{user_input}\"")
        print(f"{'─' * 80}")
        
        # Test with LLM
        if interpreter_llm.use_llm:
            print("\n🤖 LLM-based interpretation:")
            llm_result = interpreter_llm.interpret(user_input)
            print(f"   Goal:       {llm_result.get('goal')}")
            print(f"   Confidence: {llm_result.get('confidence', 0):.2f}")
            print(f"   Reasoning:  {llm_result.get('reasoning', 'N/A')}")
        else:
            print("\n⚠️  LLM not available (check API key and dependencies)")
        
        # Test with rule-based for comparison
        print("\n📋 Rule-based interpretation:")
        rule_result = interpreter_rules.interpret(user_input)
        print(f"   Goal:       {rule_result.get('goal')}")
        print(f"   Confidence: {rule_result.get('confidence', 0):.2f}")
        
        # Validation
        if interpreter_llm.use_llm:
            is_valid_llm = interpreter_llm.validate_interpretation(llm_result, min_confidence=0.70)
            is_valid_rule = interpreter_rules.validate_interpretation(rule_result, min_confidence=0.70)
            
            print(f"\n✓ LLM Valid (>0.70):  {'Yes ✓' if is_valid_llm else 'No ✗'}")
            print(f"✓ Rule Valid (>0.70): {'Yes ✓' if is_valid_rule else 'No ✗'}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    
    # Summary
    if interpreter_llm.use_llm:
        print("\n✅ LLM integration is working!")
        print("   The agent can now understand natural language like 'I want to use brave'")
        print("   and correctly identify which application to launch.")
    else:
        print("\n⚠️  LLM integration not active")
        print("   Reasons:")
        print("   - GROQ_API_KEY not set in .env file")
        print("   - LangChain dependencies not installed")
        print("   - use_llm=False in configuration")


def interactive_test():
    """Interactive testing mode."""
    print("\n" + "=" * 80)
    print("INTERACTIVE LLM TEST MODE")
    print("=" * 80)
    
    interpreter = NaturalLanguageInterpreter(use_llm=True)
    
    if not interpreter.use_llm:
        print("\n⚠️  LLM not available. See LLM_SETUP.md for setup instructions.")
        return
    
    print("\nType your commands to see how the LLM interprets them.")
    print("Type 'quit' to exit.\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            result = interpreter.interpret(user_input)
            
            print(f"\n🤖 LLM Interpretation:")
            print(f"   Goal:       {result.get('goal')}")
            print(f"   Confidence: {result.get('confidence', 0):.2f}")
            print(f"   Reasoning:  {result.get('reasoning', 'N/A')}")
            
            is_valid = interpreter.validate_interpretation(result, min_confidence=0.70)
            print(f"   Valid:      {'Yes ✓' if is_valid else 'No ✗'}")
            print()
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")
    
    print("\nGoodbye!")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Test LLM interpreter')
    parser.add_argument('--interactive', '-i', action='store_true', 
                       help='Run in interactive mode')
    
    args = parser.parse_args()
    
    if args.interactive:
        interactive_test()
    else:
        test_interpreter()
