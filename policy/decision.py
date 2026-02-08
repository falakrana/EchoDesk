"""
Policy Decision Engine

This module maps structured goals (from LLM) to allowed applications (from registry).
It acts as the bridge between intent and execution, enforcing security policies.

SECURITY CONSTRAINTS:
- Input: Structured goal (string) from LLM
- Output: Friendly app name (string) that exists in registry
- NEVER constructs file paths or commands
- NEVER executes anything
- Read-only access to app registry

The policy engine enforces the "what" without knowing the "how".
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class PolicyDecisionEngine:
    """
    Maps goals to allowed applications based on policy rules.
    
    This class sits between the LLM interpreter and the registry validator.
    It knows WHAT the user wants to do, and decides WHICH app should handle it,
    but it never knows WHERE that app is located.
    """
    
    # Goal-to-App mapping policy
    # This defines which goals map to which friendly app names
    GOAL_TO_APP_POLICY = {
        # Text editing goals
        'write_text': ['notepad', 'notepadplusplus', 'vscode', 'sublime'],
        'edit_text': ['notepad', 'notepadplusplus', 'vscode', 'sublime'],
        'take_notes': ['notepad', 'notepadplusplus', 'onenote'],
        
        # Web browsing goals
        'browse_web': ['chrome', 'firefox', 'edge', 'brave'],
        'search_web': ['chrome', 'firefox', 'edge', 'brave'],
        'chrome': ['chrome'],
        'google chrome': ['chrome'],
        'brave browser': ['brave'],
        'edge browser': ['edge'],
        'firefox browser': ['firefox'],
        
        # Code editing goals
        'code': ['vscode', 'sublime', 'atom', 'notepadplusplus'],
        'program': ['vscode', 'sublime', 'atom', 'pycharm', 'intellij'],
        'develop': ['vscode', 'sublime', 'atom', 'pycharm', 'intellij'],
        'vscode': ['vscode'],
        'visual studio code': ['vscode'],
        
        # Email goals
        'email': ['outlook', 'thunderbird'],
        'mail': ['outlook', 'thunderbird'],
        
        # Chat/Communication goals
        'chat': ['slack', 'teams', 'discord', 'telegram'],
        'message': ['slack', 'teams', 'discord', 'telegram'],
        
        # Media goals
        'media': ['vlc', 'spotify', 'itunes', 'winamp'],
        'music': ['spotify', 'itunes', 'vlc', 'winamp'],
        'video': ['vlc', 'mpv', 'mpc'],
        
        # Design goals
        'design': ['gimp', 'inkscape', 'photoshop', 'illustrator'],
        'edit_image': ['gimp', 'paint', 'photoshop'],
        'edit_photo': ['gimp', 'photoshop', 'lightroom'],
        
        # Office goals
        'word_processing': ['word', 'libreoffice', 'openoffice'],
        'spreadsheet': ['excel', 'libreoffice', 'openoffice'],
        'presentation': ['powerpoint', 'libreoffice', 'openoffice'],
    }
    
    def __init__(self, registry_path: Optional[Path] = None):
        """
        Initialize the policy engine.
        
        Args:
            registry_path: Path to app_registry.json (optional, for validation)
        """
        self.registry_path = registry_path
        self.available_apps: Optional[List[str]] = None
        
        # Load available apps if registry path provided
        if registry_path and registry_path.exists():
            self._load_available_apps()
    
    def _load_available_apps(self) -> None:
        """
        Load the list of available apps from the registry.
        
        This is used for intelligent fallback selection.
        """
        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                registry_data = json.load(f)
                self.available_apps = list(registry_data.get('applications', {}).keys())
                logger.info(f"Loaded {len(self.available_apps)} available apps from registry")
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
            self.available_apps = []
    
    def _extract_app_from_goal(self, goal: str) -> Optional[str]:
        """
        Extract direct app name from goals like "launch_chrome".
        
        Args:
            goal: Goal string (e.g., "launch_chrome")
            
        Returns:
            App name if goal is a direct launch, None otherwise
        """
        if goal and goal.startswith('launch_'):
            app_name = goal.replace('launch_', '')
            logger.info(f"Direct app launch detected: {app_name}")
            return app_name
        
        return None
    
    def decide(self, goal: str) -> Optional[str]:
        """
        Decide which application should handle the given goal.
        
        This method implements the core policy logic:
        1. Check if goal is a direct app launch (e.g., "launch_chrome")
        2. Look up goal in policy mapping
        3. Select first available app from policy list
        4. Return app name (NOT path)
        
        Args:
            goal: Structured goal from LLM (e.g., "write_text", "launch_chrome")
            
        Returns:
            Friendly app name (e.g., "notepad", "chrome") or None
        
        Example:
            >>> engine.decide("write_text")
            "notepad"
            
            >>> engine.decide("launch_chrome")
            "chrome"
        """
        if not goal:
            logger.warning("Empty goal provided")
            return None
        
        logger.info(f"Making policy decision for goal: {goal}")
        
        # Check for direct app launch
        direct_app = self._extract_app_from_goal(goal)
        if direct_app:
            # Validate against available apps if registry is loaded
            if self.available_apps is not None:
                if direct_app in self.available_apps:
                    logger.info(f"Decision: {direct_app} (direct launch, validated)")
                    return direct_app
                else:
                    logger.warning(f"App '{direct_app}' not found in registry, checking policy mapping...")
                    # Fall through to policy lookup if direct app not in registry
            else:
                # No registry loaded, trust the goal
                logger.info(f"Decision: {direct_app} (direct launch, unvalidated)")
                return direct_app
        
        # Look up goal (or direct app name) in policy mapping
        candidate_apps = self.GOAL_TO_APP_POLICY.get(goal, [])
        
        # If no candidates found for the full goal, try the direct app name if it exists
        if not candidate_apps and direct_app and direct_app != goal:
            candidate_apps = self.GOAL_TO_APP_POLICY.get(direct_app, [])
        
        if not candidate_apps:
            logger.warning(f"No policy mapping found for goal: {goal}")
            return None
        
        # Select first available app from candidates
        if self.available_apps is not None:
            # Filter candidates by availability
            for app in candidate_apps:
                if app in self.available_apps:
                    logger.info(f"Decision: {app} (from policy, validated)")
                    return app
            
            logger.warning(f"None of the candidate apps {candidate_apps} are available")
            return None
        else:
            # No registry loaded, return first candidate
            selected_app = candidate_apps[0]
            logger.info(f"Decision: {selected_app} (from policy, unvalidated)")
            return selected_app
    
    def explain_decision(self, goal: str) -> Dict[str, any]:
        """
        Explain the decision-making process for a goal.
        
        Useful for debugging and transparency.
        
        Args:
            goal: Goal to explain
            
        Returns:
            Dictionary with decision explanation
        """
        explanation = {
            'goal': goal,
            'decision': None,
            'reasoning': [],
            'candidates': [],
            'available': self.available_apps is not None
        }
        
        # Check direct launch
        direct_app = self._extract_app_from_goal(goal)
        if direct_app:
            explanation['reasoning'].append(f"Direct app launch detected: {direct_app}")
            explanation['candidates'] = [direct_app]
            
            if self.available_apps and direct_app in self.available_apps:
                explanation['decision'] = direct_app
                explanation['reasoning'].append(f"App '{direct_app}' found in registry")
            elif self.available_apps:
                explanation['reasoning'].append(f"App '{direct_app}' NOT found in registry")
            else:
                explanation['decision'] = direct_app
                explanation['reasoning'].append("Registry not loaded, trusting goal")
            
            return explanation
        
        # Policy lookup
        candidate_apps = self.GOAL_TO_APP_POLICY.get(goal, [])
        explanation['candidates'] = candidate_apps
        
        if not candidate_apps:
            explanation['reasoning'].append(f"No policy mapping for goal: {goal}")
            return explanation
        
        explanation['reasoning'].append(f"Policy candidates: {candidate_apps}")
        
        # Selection
        if self.available_apps:
            for app in candidate_apps:
                if app in self.available_apps:
                    explanation['decision'] = app
                    explanation['reasoning'].append(f"Selected '{app}' (first available)")
                    break
            
            if not explanation['decision']:
                explanation['reasoning'].append("No candidates available in registry")
        else:
            explanation['decision'] = candidate_apps[0]
            explanation['reasoning'].append(f"Selected '{candidate_apps[0]}' (first candidate, registry not loaded)")
        
        return explanation


# Example usage and testing
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Test without registry
    print("\n" + "=" * 60)
    print("POLICY ENGINE TEST (No Registry)")
    print("=" * 60)
    
    engine = PolicyDecisionEngine()
    
    test_goals = [
        'write_text',
        'browse_web',
        'launch_chrome',
        'code',
        'email',
        'unknown_goal',
    ]
    
    for goal in test_goals:
        decision = engine.decide(goal)
        explanation = engine.explain_decision(goal)
        
        print(f"\nGoal: {goal}")
        print(f"Decision: {decision}")
        print(f"Reasoning: {' → '.join(explanation['reasoning'])}")
