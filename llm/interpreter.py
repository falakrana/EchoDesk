"""
Phase 2: LLM-based Natural Language Interpreter

This module takes raw user text and converts it into a structured goal.
It NEVER sees file paths, executables, or generated commands.

SECURITY CONSTRAINTS:
- Input: Raw natural language text only
- Output: Structured JSON with goal and confidence
- NEVER receives file paths or executable names
- NEVER constructs system commands
- NEVER executes anything

The LLM's ONLY job is to understand user intent, not to make execution decisions.
"""

import json
import re
import os
from typing import Any, Dict, Optional
import logging
from dotenv import load_dotenv

# LangChain imports
try:
    from langchain_groq import ChatGroq
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import PydanticOutputParser
    from pydantic import BaseModel, Field
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    logging.warning("LangChain not available. Install with: pip install -r requirements.txt")

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


# Pydantic model for LLM output (only if LangChain is available)
if LANGCHAIN_AVAILABLE:
    class IntentOutput(BaseModel):
        """Structured output from LLM interpretation."""
        goal: str = Field(description="The user's goal or intent, e.g., 'browse_web', 'write_text', or 'launch_<app_name>'")
        app_name: Optional[str] = Field(default=None, description="Specific application name mentioned by user, if any (e.g., 'brave', 'chrome', 'notepad')")
        confidence: float = Field(description="Confidence score between 0.0 and 1.0")
        reasoning: str = Field(description="Brief explanation of why this interpretation was chosen")


class NaturalLanguageInterpreter:
    """
    Converts natural language input into structured goals.
    
    This class uses rule-based NLP (with optional LLM enhancement) to extract
    user intent from natural language. It operates in complete isolation from
    the execution layer.
    
    CRITICAL: This module NEVER sees:
    - File paths
    - Executable names
    - System commands
    - Registry contents
    """
    
    # Intent patterns for rule-based extraction
    INTENT_PATTERNS = {
        'write_text': [
            r'(?:write|type|edit|create)\s+(?:a\s+)?(?:note|text|document|file)',
            r'i\s+(?:want|need)\s+to\s+(?:write|type|take)\s+(?:notes?|text)',
            r'(?:open|start)\s+(?:a\s+)?(?:text\s+editor|notepad)',
        ],
        'browse_web': [
            r'(?:open|launch|start)\s+(?:a\s+)?(?:browser|web\s+browser)',
            r'(?:browse|surf|search)\s+(?:the\s+)?(?:web|internet)',
            r'i\s+(?:want|need)\s+to\s+(?:browse|search|look\s+up)',
        ],
        'code': [
            r'(?:write|edit|create)\s+(?:some\s+)?code',
            r'(?:open|launch|start)\s+(?:a\s+)?(?:code\s+editor|ide)',
            r'i\s+(?:want|need)\s+to\s+(?:code|program|develop)',
        ],
        'email': [
            r'(?:check|read|send|write)\s+(?:my\s+)?(?:email|mail)',
            r'(?:open|launch|start)\s+(?:my\s+)?(?:email|mail)\s+(?:client|app)',
        ],
        'chat': [
            r'(?:open|launch|start)\s+(?:slack|teams|discord|chat)',
            r'i\s+(?:want|need)\s+to\s+(?:chat|message|talk)',
        ],
        'media': [
            r'(?:play|watch|listen|view)\s+(?:music|video|media)',
            r'(?:open|launch|start)\s+(?:a\s+)?(?:media\s+player|music\s+player)',
        ],
        'design': [
            r'(?:edit|create|design)\s+(?:image|photo|graphic|design)',
            r'(?:open|launch|start)\s+(?:photoshop|gimp|inkscape|illustrator)',
        ],
    }
    
    def __init__(self, use_llm: bool = True, llm_model: Optional[str] = None):
        """
        Initialize the interpreter.
        
        Args:
            use_llm: Whether to use LLM for enhanced interpretation (default: True)
            llm_model: LLM model to use
        """
        self.use_llm = use_llm and LANGCHAIN_AVAILABLE
        self.llm_model = llm_model or "llama-3.1-8b-instant"
        self.llm = None
        self.llm_chain = None
        
        # Initialize LLM if requested and available
        if self.use_llm:
            try:
                api_key = os.getenv("GROQ_API_KEY")
                if not api_key or api_key == "your_api_key_here":
                    logger.warning("GROQ_API_KEY not set. Create a .env file with your API key.")
                    logger.warning("Falling back to rule-based extraction.")
                    self.use_llm = False
                else:
                    self.llm = ChatGroq(
                        model=self.llm_model,
                        api_key=api_key,
                        temperature=0.1,
                    )
                    
                    # Create output parser
                    self.parser = PydanticOutputParser(pydantic_object=IntentOutput)
                    
                    # Create prompt template
                    self.prompt_template = PromptTemplate(
                        template="""You are an intent classifier for a desktop application launcher.

Your job is to understand what the user wants to do and extract:
1. The user's goal (e.g., browse_web, write_text, code, email, chat, media, design)
2. Any specific application name they mentioned (e.g., brave, chrome, notepad, vscode)
3. Your confidence in this interpretation (0.0 to 1.0)

IMPORTANT RULES:
- If the user mentions a specific app name, use goal format: "launch_<app_name>" (e.g., "launch_brave")
- Common goals: browse_web, write_text, code, email, chat, media, design
- Be confident (0.8+) only when the intent is clear
- If ambiguous, lower the confidence score

User input: "{user_input}"

{format_instructions}

Respond with valid JSON only.""",
                        input_variables=["user_input"],
                        partial_variables={"format_instructions": self.parser.get_format_instructions()}
                    )
                    
                    logger.info(f"LLM initialized: {self.llm_model}")
                    
            except Exception as e:
                logger.error(f"Failed to initialize LLM: {e}")
                logger.warning("Falling back to rule-based extraction.")
                self.use_llm = False
        else:
            logger.info("Using rule-based extraction (LLM disabled)")
    
    def _extract_goal_rule_based(self, user_input: str) -> Optional[str]:
        """
        Extract goal using rule-based pattern matching.
        
        Args:
            user_input: Raw user text
            
        Returns:
            Goal string (e.g., "write_text", "browse_web", "chat") or None
        """
        # Strip punctuation and normalize
        user_input_lower = user_input.lower().strip()
        # Remove common punctuation at the end
        user_input_lower = re.sub(r'[.!?,;]+$', '', user_input_lower)
        
        # Check for conversational/greeting patterns first
        greeting_patterns = [
            r'^(hi|hello|hey|greetings|good\s+(morning|afternoon|evening))[\s!]*$',
            r'^(how\s+are\s+you|what\'?s\s+up|wassup)[\s?!]*$',
            r'^(thanks?|thank\s+you|thx)[\s!]*$',
            r'^(bye|goodbye|see\s+you|cya)[\s!]*$',
        ]
        
        for pattern in greeting_patterns:
            if re.search(pattern, user_input_lower):
                logger.info("Detected conversational greeting/chat")
                return "chat"
        
        # Check for questions about the agent itself
        agent_question_patterns = [
            r'(what|who)\s+(are|is)\s+you',
            r'what\s+can\s+you\s+do',
            r'help\s+me',
            r'how\s+do\s+(i|you)',
        ]
        
        for pattern in agent_question_patterns:
            if re.search(pattern, user_input_lower):
                logger.info("Detected question about agent capabilities")
                return "chat"
        
        # Try to match against intent patterns
        for goal, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, user_input_lower):
                    logger.info(f"Matched goal: {goal}")
                    return goal
        
        # Try to extract app name directly with more flexible matching
        # Match: "I want to use/open/launch <app>" or just "use/open/launch <app>"
        direct_match = re.search(
            r'(?:i\s+(?:want|need|would\s+like)\s+to\s+)?(?:open|launch|start|run|use)\s+([\w\s]+)',
            user_input_lower
        )
        
        if direct_match:
            app_name = direct_match.group(1).strip()
            # Clean up common trailing words
            app_name = re.sub(r'\s+(now|please|pls|plz)$', '', app_name)
            logger.info(f"Direct app mention: {app_name}")
            return f"launch_{app_name}"
        
        # If nothing matched, it might be a general chat message
        logger.info("No specific intent matched - treating as chat")
        return "chat"
    
    def _extract_goal_llm(self, user_input: str) -> Dict[str, Any]:
        """
        Extract goal using LLM (Groq).
        
        Args:
            user_input: Raw user text
            
        Returns:
            Dictionary with goal, confidence, and reasoning
        """
        try:
            # Create the prompt
            prompt = self.prompt_template.format(user_input=user_input)
            
            # Get LLM response
            response = self.llm.invoke(prompt)
            
            # Parse the response
            parsed_output = self.parser.parse(response.content)
            
            # If app_name is specified, use launch_<app_name> format
            if parsed_output.app_name:
                goal = f"launch_{parsed_output.app_name.lower().replace(' ', '_')}"
            else:
                goal = parsed_output.goal
            
            logger.info(f"LLM extracted goal: {goal} (confidence: {parsed_output.confidence:.2f})")
            logger.info(f"LLM reasoning: {parsed_output.reasoning}")
            
            return {
                "goal": goal,
                "confidence": parsed_output.confidence,
                "reasoning": parsed_output.reasoning
            }
            
        except Exception as e:
            logger.error(f"LLM extraction failed: {e}")
            logger.warning("Falling back to rule-based extraction")
            
            # Fallback to rule-based
            goal = self._extract_goal_rule_based(user_input)
            confidence = self._calculate_confidence(user_input, goal)
            
            return {
                "goal": goal,
                "confidence": confidence,
                "reasoning": "LLM failed, used rule-based fallback"
            }
    
    
    def _calculate_confidence(self, user_input: str, goal: Optional[str]) -> float:
        """
        Calculate confidence score for the extracted goal.
        
        Args:
            user_input: Original user input
            goal: Extracted goal
            
        Returns:
            Confidence score between 0.0 and 1.0
        """
        if goal is None:
            return 0.0
        
        # High confidence for chat intents (they're clearly conversational)
        if goal == 'chat':
            return 0.95
        
        # Base confidence
        confidence = 0.5
        
        # Increase confidence for clear action verbs
        action_verbs = ['open', 'launch', 'start', 'run', 'use']
        if any(verb in user_input.lower() for verb in action_verbs):
            confidence += 0.2
        
        # Increase confidence for specific app mentions
        if goal.startswith('launch_'):
            confidence += 0.2
        
        # Decrease confidence for ambiguous input
        if len(user_input.split()) > 10:
            confidence -= 0.1
        
        # Ensure confidence is in valid range
        return max(0.0, min(1.0, confidence))
    
    def interpret(self, user_input: str) -> Dict[str, Any]:
        """
        Interpret natural language input into a structured goal.
        
        This is the ONLY public method. It returns a structured JSON object
        that contains ONLY the goal and confidence. No paths, no commands.
        
        Args:
            user_input: Raw natural language text from user
            
        Returns:
            Dictionary with:
                - goal: String describing user intent (e.g., "write_text", "launch_brave")
                - confidence: Float between 0.0 and 1.0
                - raw_input: Original input (for logging only)
                - reasoning: Explanation of interpretation (if LLM used)
        
        Example:
            >>> interpreter.interpret("I want to use brave")
            {
                "goal": "launch_brave",
                "confidence": 0.95,
                "raw_input": "I want to use brave",
                "reasoning": "User explicitly mentioned 'brave' browser"
            }
        """
        logger.info(f"Interpreting: {user_input}")
        
        # Use LLM if available, otherwise fall back to rule-based
        if self.use_llm and self.llm is not None:
            logger.info("Using LLM-based extraction")
            llm_result = self._extract_goal_llm(user_input)
            
            result = {
                "goal": llm_result.get("goal"),
                "confidence": llm_result.get("confidence", 0.0),
                "raw_input": user_input,
                "reasoning": llm_result.get("reasoning", "")
            }
        else:
            logger.info("Using rule-based extraction")
            # Extract goal using rule-based approach
            goal = self._extract_goal_rule_based(user_input)
            
            # Calculate confidence
            confidence = self._calculate_confidence(user_input, goal)
            
            # Build structured response
            result = {
                "goal": goal,
                "confidence": confidence,
                "raw_input": user_input,
                "reasoning": "Rule-based pattern matching"
            }
        
        logger.info(f"Interpretation result: goal={result['goal']}, confidence={result['confidence']:.2f}")
        
        return result
    
    def validate_interpretation(self, interpretation: Dict[str, Any], 
                              min_confidence: float = 0.85) -> bool:
        """
        Validate that an interpretation meets minimum confidence threshold.
        
        Args:
            interpretation: Result from interpret()
            min_confidence: Minimum required confidence (default: 0.85)
            
        Returns:
            True if interpretation is valid and confident enough
        """
        if interpretation.get('goal') is None:
            logger.warning("No goal extracted from input")
            return False
        
        confidence = interpretation.get('confidence', 0.0)
        if confidence < min_confidence:
            logger.warning(f"Confidence {confidence:.2f} below threshold {min_confidence}")
            return False
        
        return True
    
    def generate_chat_response(self, user_input: str) -> str:
        """
        Generate a conversational response for chat-type inputs.
        
        Args:
            user_input: Original user input
            
        Returns:
            Friendly conversational response
        """
        user_input_lower = user_input.lower().strip()
        
        # Greetings
        if re.search(r'^(hi|hello|hey)', user_input_lower):
            return "Hello! I'm your AI Desktop Agent. I can help you launch applications. Just tell me what you'd like to open!"
        
        if re.search(r'good\s+(morning|afternoon|evening)', user_input_lower):
            return "Good day! How can I help you today? I can launch any installed application for you."
        
        # How are you
        if re.search(r'how\s+are\s+you', user_input_lower):
            return "I'm doing great, thanks for asking! Ready to help you launch applications. What would you like to open?"
        
        # What's up
        if re.search(r'what\'?s\s+up|wassup', user_input_lower):
            return "Not much! Just here to help you launch applications. What do you need?"
        
        # Thanks
        if re.search(r'thanks?|thank\s+you', user_input_lower):
            return "You're welcome! Let me know if you need anything else."
        
        # Goodbye
        if re.search(r'bye|goodbye|see\s+you', user_input_lower):
            return "Goodbye! Have a great day!"
        
        # What are you / Who are you
        if re.search(r'(what|who)\s+(are|is)\s+you', user_input_lower):
            return "I'm an AI Desktop Agent designed to help you launch applications using natural language. Just tell me what app you want to open!"
        
        # What can you do
        if re.search(r'what\s+can\s+you\s+do', user_input_lower):
            return "I can launch any installed application on your computer! Just say something like 'open Chrome' or 'I want to use Notepad'. Type 'list' to see all available apps."
        
        # Help me
        if re.search(r'help\s+me', user_input_lower):
            return "Sure! I can help you launch applications. Try saying things like:\n  • 'Open Chrome'\n  • 'I want to use Brave'\n  • 'Launch Notepad'\n\nType 'list' to see all available applications, or 'help' for more commands."
        
        # Default friendly response
        return "I'm here to help you launch applications! Try saying something like 'open Chrome' or 'launch Notepad'. Type 'list' to see what's available."


# Example usage and testing
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    interpreter = NaturalLanguageInterpreter()
    
    test_inputs = [
        "I want to write notes",
        "open chrome",
        "can you launch vscode",
        "I need to check my email",
        "start spotify",
        "delete all my files",  # Should fail
        "hello world",  # Should fail
    ]
    
    print("\n" + "=" * 60)
    print("LLM INTERPRETER TEST")
    print("=" * 60)
    
    for user_input in test_inputs:
        result = interpreter.interpret(user_input)
        is_valid = interpreter.validate_interpretation(result)
        
        print(f"\nInput: {user_input}")
        print(f"Goal: {result['goal']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Valid: {'✓' if is_valid else '✗'}")
