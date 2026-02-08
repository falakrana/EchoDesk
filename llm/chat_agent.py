"""
Conversational AI Agent with Application Launch Capabilities

This module creates a full conversational AI assistant that can:
1. Chat naturally about anything
2. Launch applications when requested
3. Use LLM (Groq) to decide when to chat vs. when to take action

The LLM has access to a "launch_application" tool that it can call
when the user wants to open an application.
"""

import os
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path
from dotenv import load_dotenv

# LangChain imports
try:
    from langchain_groq import ChatGroq
    from langchain_core.tools import tool
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logging.warning("LangChain not available. Install with: pip install -r requirements.txt")

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class ConversationalAgent:
    """
    A conversational AI agent that can chat and launch applications.
    
    This agent uses a Groq-hosted LLM with function calling to:
    - Have natural conversations
    - Detect when user wants to launch an app
    - Call the appropriate tool to launch apps
    """
    
    def __init__(self, registry_path: Optional[Path] = None, llm_model: str = "llama-3.1-8b-instant"):
        """
        Initialize the conversational agent.
        
        Args:
            registry_path: Path to app_registry.json
            llm_model: LLM model to use
        """
        self.llm_model = llm_model
        self.llm = None
        self.chat_history: List[Any] = []
        self.available_apps: Dict[str, str] = {}
        self.launch_tool = None
        
        # Load registry
        if registry_path and registry_path.exists():
            self._load_registry(registry_path)
        
        # Initialize LLM and agent
        if LANGCHAIN_AVAILABLE:
            self._initialize_agent()
        else:
            logger.error("LangChain not available. Cannot create conversational agent.")
    
    def _load_registry(self, registry_path: Path) -> None:
        """Load application registry."""
        try:
            with open(registry_path, 'r', encoding='utf-8') as f:
                registry_data = json.load(f)
            self.available_apps = registry_data.get('applications', {})
            logger.info(f"Loaded {len(self.available_apps)} applications")
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
    
    def _create_launch_tool(self):
        """
        Create a tool for launching applications.
        
        This tool will be available to the LLM to call when needed.
        """
        available_apps = self.available_apps
        
        @tool
        def launch_application(app_name: str) -> str:
            """Launch an application by name. Use this when the user wants to open, launch, start, or use an application.
            
            Args:
                app_name: Name of the application to launch (e.g., 'chrome', 'notepad', 'brave')
            
            Returns:
                JSON string with launch status
            
            Examples:
                - User: "open chrome" -> call launch_application("chrome")
                - User: "I want to use brave" -> call launch_application("brave")
                - User: "launch notepad" -> call launch_application("notepad")
            """
            app_name_lower = app_name.lower().strip()
            
            # Try exact match first
            if app_name_lower in available_apps:
                return json.dumps({
                    "action": "launch",
                    "app_name": app_name_lower,
                    "status": "success",
                    "message": f"Launching {app_name_lower}"
                })
            
            # Try fuzzy match (contains)
            for app in available_apps.keys():
                if app_name_lower in app or app in app_name_lower:
                    return json.dumps({
                        "action": "launch",
                        "app_name": app,
                        "status": "success",
                        "message": f"Launching {app}"
                    })
            
            # App not found
            available_list = ", ".join(list(available_apps.keys())[:10])
            return json.dumps({
                "action": "launch",
                "app_name": app_name_lower,
                "status": "error",
                "message": f"Application '{app_name}' not found. Try: {available_list}..."
            })
        
        return launch_application
    
    def _initialize_agent(self) -> None:
        """Initialize the LLM and bind tools."""
        try:
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key or api_key == "your_api_key_here":
                logger.error("GROQ_API_KEY not set. Please create a .env file with your API key.")
                return
            
            self.launch_tool = self._create_launch_tool()
            self.llm = ChatGroq(
                model=self.llm_model,
                api_key=api_key,
                temperature=0.7,
            ).bind_tools([self.launch_tool])
            
            logger.info(f"Conversational agent initialized with {self.llm_model}")
            
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            logger.exception(e)
    
    def chat(self, user_input: str) -> Dict[str, Any]:
        """
        Process user input and generate a response.
        
        The LLM will decide whether to:
        1. Just chat (return a conversational response)
        2. Launch an app (call the launch_application tool)
        
        Args:
            user_input: User's message
            
        Returns:
            Dictionary with response and any actions taken
        """
        if not self.llm or not self.launch_tool:
            return {
                "response": "Sorry, I'm not properly initialized. Please check your GROQ_API_KEY.",
                "action": None,
                "error": "Agent not initialized"
            }
        
        try:
            app_list = ", ".join(list(self.available_apps.keys())[:20])
            if len(self.available_apps) > 20:
                app_list += f"... and {len(self.available_apps) - 20} more"
            
            system_prompt = """You are a helpful AI assistant that can chat naturally AND launch applications on the user's computer.

Your capabilities:
1. Have natural conversations about anything (weather, jokes, questions, advice, etc.)
2. Launch applications when the user requests it

When to use the launch_application tool:
- User explicitly asks to open/launch/start/use an application
- Examples: "open chrome", "I want to use brave", "launch notepad"

When to just chat:
- Greetings: "hello", "hi", "how are you"
- Questions: "what's the weather?", "tell me a joke"
- General conversation: "what can you do?", "help me with..."

Be friendly, helpful, and conversational. If you're not sure which app the user wants, ask for clarification.

Available applications: {app_list}
""".format(app_list=app_list)

            messages: List[Any] = [SystemMessage(content=system_prompt)]
            messages.extend(self.chat_history)
            messages.append(HumanMessage(content=user_input))

            first_response = self.llm.invoke(messages)

            action_taken = None
            final_text = first_response.content if hasattr(first_response, "content") else ""

            tool_calls = getattr(first_response, "tool_calls", None) or []
            if tool_calls:
                tool_messages: List[ToolMessage] = []

                for tool_call in tool_calls:
                    tool_name = tool_call.get("name")
                    tool_call_id = tool_call.get("id")
                    tool_args = tool_call.get("args")

                    if tool_args is None:
                        function = tool_call.get("function") or {}
                        arguments = function.get("arguments")
                        if isinstance(arguments, str):
                            try:
                                tool_args = json.loads(arguments)
                            except Exception:
                                tool_args = {}

                    if tool_name != self.launch_tool.name:
                        continue

                    tool_output = self.launch_tool.invoke(tool_args or {})
                    tool_messages.append(ToolMessage(content=tool_output, tool_call_id=tool_call_id))

                    try:
                        action_data = json.loads(tool_output)
                        if action_data.get("action") == "launch":
                            action_taken = action_data
                    except Exception:
                        pass

                followup_messages: List[Any] = messages + [first_response] + tool_messages
                final_response = self.llm.invoke(followup_messages)
                final_text = final_response.content if hasattr(final_response, "content") else final_text

            self.chat_history.append(HumanMessage(content=user_input))
            self.chat_history.append(AIMessage(content=final_text))

            if len(self.chat_history) > 10:
                self.chat_history = self.chat_history[-10:]
            
            return {
                "response": final_text,
                "action": action_taken,
                "error": None
            }
            
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            logger.exception(e)
            return {
                "response": f"Sorry, I encountered an error: {str(e)}",
                "action": None,
                "error": str(e)
            }
    
    def reset_history(self) -> None:
        """Clear chat history."""
        self.chat_history = []
        logger.info("Chat history cleared")


# Example usage
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Create agent
    registry_path = Path(__file__).parent.parent / 'config' / 'app_registry.json'
    agent = ConversationalAgent(registry_path=registry_path)
    
    # Test conversations
    test_inputs = [
        "Hello! How are you?",
        "What can you do?",
        "Tell me a joke",
        "I want to open chrome",
        "Thanks!",
    ]
    
    print("\n" + "=" * 70)
    print("CONVERSATIONAL AGENT TEST")
    print("=" * 70)
    
    for user_input in test_inputs:
        print(f"\n> {user_input}")
        result = agent.chat(user_input)
        print(f"🤖 {result['response']}")
        if result['action']:
            print(f"⚡ Action: {result['action']}")
