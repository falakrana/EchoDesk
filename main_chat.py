"""
AI Desktop Agent - Conversational Chat Mode

This is an alternative entry point that uses the full conversational AI agent.
The LLM handles everything - chatting AND deciding when to launch apps.

Usage:
    python main_chat.py
"""

import sys
import logging
from pathlib import Path
from typing import Optional

# Import modules
from llm.chat_agent import ConversationalAgent
from system.executor import SafeExecutor
from memory.state import AgentMemory
from ui.cli import CLI

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('agent_chat.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ChatDesktopAgent:
    """
    Conversational AI Desktop Agent.
    
    This version uses a full conversational AI that:
    - Chats naturally about anything
    - Launches apps when requested
    - Uses LLM to decide when to chat vs. act
    """
    
    def __init__(self, config_dir: Optional[Path] = None, dry_run: bool = False):
        """
        Initialize the chat agent.
        
        Args:
            config_dir: Directory containing app_registry.json
            dry_run: If True, simulate execution without launching apps
        """
        # Determine config directory
        if config_dir is None:
            config_dir = Path(__file__).parent / 'config'
        
        self.config_dir = Path(config_dir)
        self.registry_path = self.config_dir / 'app_registry.json'
        self.memory_path = self.config_dir / 'memory.json'
        self.dry_run = dry_run
        
        # Initialize modules
        self.cli = CLI()
        self.executor = SafeExecutor(dry_run=dry_run)
        self.memory = AgentMemory(persist_path=self.memory_path)
        
        # Check registry exists
        if not self.registry_path.exists():
            self.cli.show_error("Application registry not found!")
            self.cli.show_warning("Please run bootstrap scan first:")
            self.cli.show_info("  python -m tools.bootstrap_scan")
            sys.exit(1)
        
        # Initialize conversational agent
        self.agent = ConversationalAgent(
            registry_path=self.registry_path,
            llm_model="llama-3.1-8b-instant"
        )
        
        logger.info("Chat Desktop Agent initialized")
    
    def _handle_special_command(self, user_input: str) -> bool:
        """
        Handle special commands (help, list, stats, exit, clear).
        
        Args:
            user_input: User input string
            
        Returns:
            True if command was handled, False otherwise
        """
        command = user_input.lower().strip()
        
        if command in ['help', '?']:
            self._show_chat_help()
            return True
        
        elif command == 'list':
            self.cli.show_app_list(self.agent.available_apps)
            return True
        
        elif command == 'stats':
            stats = self.memory.get_stats()
            self.cli.show_stats(stats)
            return True
        
        elif command == 'clear':
            if self.cli.confirm("Clear chat history and memory?"):
                self.agent.reset_history()
                self.memory.clear()
                self.cli.show_success("Chat history and memory cleared")
            return True
        
        elif command in ['exit', 'quit', 'q']:
            return True
        
        return False
    
    def _show_chat_help(self) -> None:
        """Show help for chat mode."""
        help_text = """
╔══════════════════════════════════════════════════════════════╗
║                    CONVERSATIONAL CHAT MODE                  ║
╚══════════════════════════════════════════════════════════════╝

In this mode, you can chat naturally with the AI assistant!

💬 Chat Examples:
  "Hello! How are you?"
  "Tell me a joke"
  "What's the weather like?"
  "What can you do?"
  "Help me with something"

🚀 Launch Apps:
  "I want to open Chrome"
  "Can you launch Brave for me?"
  "Open notepad please"
  "Start VS Code"

🛠️ Special Commands:
  help     - Show this help message
  list     - List all available applications
  stats    - Show agent statistics
  clear    - Clear chat history and memory
  exit     - Exit the agent

The AI will decide whether to chat or launch an app based on what you say!
        """
        print(self.cli._colorize(help_text, 'blue'))
    
    def process_chat(self, user_input: str) -> None:
        """
        Process user input through the conversational agent.
        
        Args:
            user_input: User's message
        """
        logger.info(f"Processing chat: {user_input}")
        
        # Get response from conversational agent
        result = self.agent.chat(user_input)
        
        response = result.get('response', '')
        action = result.get('action')
        error = result.get('error')
        
        # Handle errors
        if error:
            self.cli.show_error(f"Error: {error}")
            self.memory.record(user_input, "error", 0.0, None, False, error)
            return
        
        # Display response
        if response:
            self.cli.show_chat_response(response)
        
        # Handle action (app launch)
        if action and action.get('status') == 'success':
            app_name = action.get('app_name')
            
            # Get executable path
            executable_path = self.agent.available_apps.get(app_name)
            
            if executable_path:
                # Execute the app
                exec_result = self.executor.execute(executable_path)
                
                if exec_result['success']:
                    self.cli.show_success(f"✓ Launched {app_name}")
                else:
                    self.cli.show_error(f"Failed to launch {app_name}: {exec_result['message']}")
                
                # Record in memory
                self.memory.record(
                    user_input=user_input,
                    goal=f"launch_{app_name}",
                    confidence=1.0,
                    app_name=app_name,
                    success=exec_result['success'],
                    message=exec_result['message']
                )
            else:
                self.cli.show_error(f"App '{app_name}' not found in registry")
        else:
            # Just a chat interaction
            self.memory.record(
                user_input=user_input,
                goal="chat",
                confidence=1.0,
                app_name=None,
                success=True,
                message="Chat response"
            )
    
    def run(self) -> None:
        """
        Main agent loop.
        """
        # Show banner
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║        AI DESKTOP AGENT - Conversational Chat Mode          ║
║                                                              ║
║  Chat naturally AND launch applications!                    ║
║  Powered by Groq                                             ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(self.cli._colorize(banner, 'cyan'))
        
        if self.dry_run:
            self.cli.show_warning("Running in DRY RUN mode - no apps will be launched")
        
        self.cli.show_info(f"Loaded {len(self.agent.available_apps)} applications")
        self.cli.show_info("Type 'help' for commands or just start chatting!")
        
        # Main loop
        while True:
            try:
                # Get user input
                user_input = self.cli.prompt_input()
                
                # Check for empty input
                if not user_input:
                    continue
                
                # Check for exit
                if user_input.lower() in ['exit', 'quit', 'q']:
                    break
                
                # Handle special commands
                if self._handle_special_command(user_input):
                    if user_input.lower() in ['exit', 'quit', 'q']:
                        break
                    continue
                
                # Process chat
                self.process_chat(user_input)
                
            except KeyboardInterrupt:
                print("\n")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                self.cli.show_error(f"An error occurred: {e}")
        
        # Show goodbye
        self.cli.show_goodbye()
        
        # Show final stats
        stats = self.memory.get_stats()
        if stats['total_interactions'] > 0:
            self.cli.show_stats(stats)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='AI Desktop Agent - Conversational Chat Mode')
    parser.add_argument('--dry-run', action='store_true', help='Simulate execution without launching apps')
    parser.add_argument('--config-dir', type=Path, help='Path to config directory')
    
    args = parser.parse_args()
    
    # Create and run agent
    agent = ChatDesktopAgent(config_dir=args.config_dir, dry_run=args.dry_run)
    agent.run()


if __name__ == '__main__':
    main()
