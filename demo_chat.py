"""
Quick interactive demo of the conversational features
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm.interpreter import NaturalLanguageInterpreter
from ui.cli import CLI

def demo():
    """Run a quick demo of conversational features"""
    interpreter = NaturalLanguageInterpreter(use_llm=False)
    cli = CLI()
    
    print("\n" + "=" * 70)
    print("CONVERSATIONAL AGENT DEMO")
    print("=" * 70)
    print("\nThis demo shows how the agent responds to different types of input.\n")
    
    test_conversations = [
        ("User greets the agent", "Hello!"),
        ("User asks what it can do", "What can you do?"),
        ("User wants to launch an app (with punctuation)", "I want to use brave."),
        ("User says thanks", "Thanks!"),
    ]
    
    for description, user_input in test_conversations:
        print(f"\n{'─' * 70}")
        print(f"Scenario: {description}")
        print(f"{'─' * 70}")
        print(f"\n> {user_input}")
        
        # Interpret
        result = interpreter.interpret(user_input)
        goal = result.get('goal')
        confidence = result.get('confidence', 0.0)
        
        # Show what happened
        if goal == 'chat':
            response = interpreter.generate_chat_response(user_input)
            cli.show_chat_response(response)
        else:
            cli.show_interpretation(goal, confidence, result.get('reasoning'))
            print(f"  → Would launch: {goal.replace('launch_', '')}")
    
    print(f"\n{'─' * 70}")
    print("\n✅ Demo complete! The agent now:")
    print("   • Responds naturally to greetings and questions")
    print("   • Handles punctuation in app launch requests")
    print("   • Provides helpful guidance")
    print("   • Still launches apps when requested")
    print("\nRun 'python main.py' to try it yourself!\n")

if __name__ == '__main__':
    demo()
