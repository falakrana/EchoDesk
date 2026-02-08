"""
Quick test of the conversational agent
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm.chat_agent import ConversationalAgent

def test_agent():
    """Test the conversational agent"""
    print("\n" + "=" * 70)
    print("TESTING CONVERSATIONAL AGENT")
    print("=" * 70)
    
    # Initialize agent
    registry_path = Path(__file__).parent / 'config' / 'app_registry.json'
    
    if not registry_path.exists():
        print(f"\n❌ Registry not found at: {registry_path}")
        print("Please run: python -m tools.bootstrap_scan")
        return
    
    print(f"\n✓ Found registry: {registry_path}")
    
    agent = ConversationalAgent(registry_path=registry_path)
    
    if not agent.llm:
        print("\n❌ Agent not initialized properly")
        print("Check your GROQ_API_KEY in .env file")
        return
    
    print(f"✓ Agent initialized with {len(agent.available_apps)} apps")
    print(f"✓ Using model: {agent.llm_model}")
    
    # Test conversations
    test_cases = [
        ("Greeting", "Hello! How are you?"),
        ("Question", "What can you do?"),
        ("App Launch", "I want to open chrome"),
    ]
    
    print("\n" + "=" * 70)
    print("RUNNING TEST CONVERSATIONS")
    print("=" * 70)
    
    for test_name, user_input in test_cases:
        print(f"\n{'─' * 70}")
        print(f"Test: {test_name}")
        print(f"{'─' * 70}")
        print(f"\n> {user_input}")
        
        try:
            result = agent.chat(user_input)
            
            print(f"\n💬 Response: {result['response']}")
            
            if result['action']:
                print(f"⚡ Action: {result['action']}")
            
            if result['error']:
                print(f"❌ Error: {result['error']}")
        
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 70)
    print("✅ TEST COMPLETE")
    print("=" * 70)
    print("\nIf all tests passed, you can run:")
    print("  python main_chat.py")
    print()

if __name__ == '__main__':
    test_agent()
