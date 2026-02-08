"""
Test the conversational chat features
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm.interpreter import NaturalLanguageInterpreter

def test_chat():
    """Test conversational interactions"""
    interpreter = NaturalLanguageInterpreter(use_llm=False)
    
    test_cases = [
        # Greetings
        "Hello!",
        "Hi there",
        "Good morning",
        "Hey",
        
        # Questions
        "How are you?",
        "What's up?",
        "What can you do?",
        "Who are you?",
        
        # Thanks
        "Thanks!",
        "Thank you",
        
        # App launches (should NOT be chat)
        "I want to use brave",
        "I want to use brave.",
        "open chrome",
        "launch notepad",
        
        # Goodbye
        "Goodbye",
        "See you later",
    ]
    
    print("\n" + "=" * 70)
    print("CONVERSATIONAL CHAT TEST")
    print("=" * 70)
    
    for user_input in test_cases:
        result = interpreter.interpret(user_input)
        goal = result.get('goal')
        confidence = result.get('confidence', 0.0)
        
        print(f"\nInput: '{user_input}'")
        print(f"  Goal: {goal}")
        print(f"  Confidence: {confidence:.2%}")
        
        if goal == 'chat':
            response = interpreter.generate_chat_response(user_input)
            print(f"  💬 Response: {response}")
        
        print()

if __name__ == '__main__':
    test_chat()
