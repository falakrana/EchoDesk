"""
Command-Line Interface for AI Desktop Agent

This module provides the user interaction layer.
It displays prompts, collects input, and shows results.

SECURITY CONSTRAINTS:
- NO business logic
- NO system calls
- NO file operations
- Pure input/output only
"""

import sys
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class CLI:
    """
    Command-line interface for the AI Desktop Agent.
    
    This class handles all user interaction but contains NO business logic.
    It simply displays information and collects input.
    """
    
    # ANSI color codes for terminal output
    COLORS = {
        'reset': '\033[0m',
        'bold': '\033[1m',
        'green': '\033[92m',
        'red': '\033[91m',
        'yellow': '\033[93m',
        'blue': '\033[94m',
        'cyan': '\033[96m',
        'gray': '\033[90m',
    }
    
    def __init__(self, use_colors: bool = True):
        """
        Initialize the CLI.
        
        Args:
            use_colors: Whether to use ANSI colors in output
        """
        self.use_colors = use_colors
    
    def _colorize(self, text: str, color: str) -> str:
        """
        Apply color to text if colors are enabled.
        
        Args:
            text: Text to colorize
            color: Color name
            
        Returns:
            Colorized text or plain text
        """
        if not self.use_colors:
            return text
        
        color_code = self.COLORS.get(color, '')
        reset_code = self.COLORS['reset']
        return f"{color_code}{text}{reset_code}"
    
    def show_banner(self) -> None:
        """Display welcome banner."""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           AI DESKTOP AGENT - Security-First Edition         ║
║                                                              ║
║  Natural Language Application Launcher for Windows          ║
║  Built with Safety by Design                                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
        """
        print(self._colorize(banner, 'cyan'))
    
    def show_help(self) -> None:
        """Display help information."""
        help_text = """
Available Commands:
  help     - Show this help message
  list     - List all available applications
  stats    - Show agent statistics
  clear    - Clear memory
  exit     - Exit the agent

Usage Examples:
  "I want to write notes"
  "open chrome"
  "launch vscode"
  "start spotify"
        """
        print(self._colorize(help_text, 'blue'))
    
    def prompt_input(self) -> str:
        """
        Prompt user for input.
        
        Returns:
            User input string
        """
        try:
            prompt = self._colorize("\n> ", 'bold')
            user_input = input(prompt).strip()
            return user_input
        except KeyboardInterrupt:
            print("\n")
            return "exit"
        except EOFError:
            return "exit"
    
    def show_success(self, message: str) -> None:
        """
        Display success message.
        
        Args:
            message: Success message to display
        """
        print(self._colorize(f"✓ {message}", 'green'))
    
    def show_error(self, message: str) -> None:
        """
        Display error message.
        
        Args:
            message: Error message to display
        """
        print(self._colorize(f"✗ {message}", 'red'))
    
    def show_warning(self, message: str) -> None:
        """
        Display warning message.
        
        Args:
            message: Warning message to display
        """
        print(self._colorize(f"⚠ {message}", 'yellow'))
    
    def show_info(self, message: str) -> None:
        """
        Display info message.
        
        Args:
            message: Info message to display
        """
        print(self._colorize(f"ℹ {message}", 'blue'))
    
    def show_interpretation(self, goal: Optional[str], confidence: float, reasoning: Optional[str] = None) -> None:
        """
        Display interpretation results.
        
        Args:
            goal: Interpreted goal
            confidence: Confidence score
            reasoning: Optional reasoning from LLM
        """
        if goal:
            conf_percent = int(confidence * 100)
            print(self._colorize(f"  🤖 Goal: {goal} (confidence: {conf_percent}%)", 'gray'))
            if reasoning:
                print(self._colorize(f"  💭 Reasoning: {reasoning}", 'gray'))
        else:
            print(self._colorize("  Could not interpret input", 'gray'))
    
    def show_chat_response(self, message: str) -> None:
        """
        Display a conversational chat response.
        
        Args:
            message: Chat response message to display
        """
        print(self._colorize(f"💬 {message}", 'cyan'))
    
    def show_app_list(self, apps: Dict[str, str]) -> None:
        """
        Display list of available applications.
        
        Args:
            apps: Dictionary of app names to paths
        """
        print(self._colorize("\nAvailable Applications:", 'bold'))
        print(self._colorize("=" * 60, 'gray'))
        
        if not apps:
            print(self._colorize("  No applications found", 'yellow'))
            print(self._colorize("  Run bootstrap scan first: python -m tools.bootstrap_scan", 'yellow'))
            return
        
        # Sort apps alphabetically
        sorted_apps = sorted(apps.keys())
        
        # Display in columns
        for i, app in enumerate(sorted_apps, 1):
            print(f"  {i:3d}. {app}")
        
        print(self._colorize("=" * 60, 'gray'))
        print(f"Total: {len(apps)} applications")
    
    def show_stats(self, stats: Dict[str, Any]) -> None:
        """
        Display agent statistics.
        
        Args:
            stats: Statistics dictionary
        """
        print(self._colorize("\nAgent Statistics:", 'bold'))
        print(self._colorize("=" * 60, 'gray'))
        
        # Session info
        print(f"  Session Start: {stats.get('session_start', 'N/A')}")
        
        # Interaction stats
        total = stats.get('total_interactions', 0)
        successful = stats.get('successful', 0)
        failed = stats.get('failed', 0)
        success_rate = stats.get('success_rate', 0.0)
        
        print(f"  Total Interactions: {total}")
        print(f"  Successful: {self._colorize(str(successful), 'green')}")
        print(f"  Failed: {self._colorize(str(failed), 'red')}")
        print(f"  Success Rate: {success_rate:.1%}")
        
        # Confidence
        avg_conf = stats.get('average_confidence', 0.0)
        print(f"  Average Confidence: {avg_conf:.1%}")
        
        # Most used apps
        most_used = stats.get('most_used_apps', {})
        if most_used:
            print(f"\n  Most Used Apps:")
            for app, count in list(most_used.items())[:5]:
                print(f"    - {app}: {count} times")
        
        print(self._colorize("=" * 60, 'gray'))
    
    def show_goodbye(self) -> None:
        """Display goodbye message."""
        goodbye = self._colorize("\nGoodbye! 👋\n", 'cyan')
        print(goodbye)
    
    def confirm(self, message: str) -> bool:
        """
        Ask user for confirmation.
        
        Args:
            message: Confirmation message
            
        Returns:
            True if user confirms, False otherwise
        """
        prompt = self._colorize(f"{message} (y/n): ", 'yellow')
        try:
            response = input(prompt).strip().lower()
            return response in ['y', 'yes']
        except (KeyboardInterrupt, EOFError):
            return False


# Example usage and testing
if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("CLI TEST")
    print("=" * 60)
    
    cli = CLI()
    
    # Test banner
    cli.show_banner()
    
    # Test messages
    cli.show_success("This is a success message")
    cli.show_error("This is an error message")
    cli.show_warning("This is a warning message")
    cli.show_info("This is an info message")
    
    # Test interpretation display
    cli.show_interpretation("write_text", 0.92)
    cli.show_interpretation(None, 0.3)
    
    # Test app list
    test_apps = {
        'notepad': 'C:\\Windows\\System32\\notepad.exe',
        'chrome': 'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
        'vscode': 'C:\\Users\\User\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe',
    }
    cli.show_app_list(test_apps)
    
    # Test stats
    test_stats = {
        'session_start': '2026-02-07T12:00:00',
        'total_interactions': 10,
        'successful': 8,
        'failed': 2,
        'success_rate': 0.8,
        'average_confidence': 0.87,
        'most_used_apps': {'notepad': 3, 'chrome': 2, 'vscode': 3}
    }
    cli.show_stats(test_stats)
