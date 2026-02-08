"""
Memory and State Management

This module tracks observations, context, and conversation history.
It provides the agent with memory of past interactions.

SECURITY CONSTRAINTS:
- Stores only observations and metadata
- NEVER stores executable paths or commands
- Read-only access to sensitive data
- No execution capabilities
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from collections import deque

logger = logging.getLogger(__name__)


@dataclass
class Observation:
    """
    Represents a single observation in the agent's memory.
    
    An observation captures what happened during an interaction:
    - User input
    - Interpreted goal
    - Decision made
    - Execution result
    - Timestamp
    """
    timestamp: str
    user_input: str
    goal: Optional[str]
    confidence: float
    app_name: Optional[str]
    success: bool
    message: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert observation to dictionary."""
        return asdict(self)


class AgentMemory:
    """
    Manages agent memory and state.
    
    This class maintains a history of observations and provides
    context for decision-making. It helps the agent learn from
    past interactions and provide better responses.
    """
    
    def __init__(self, max_history: int = 100, persist_path: Optional[Path] = None):
        """
        Initialize agent memory.
        
        Args:
            max_history: Maximum number of observations to keep in memory
            persist_path: Optional path to persist memory to disk
        """
        self.max_history = max_history
        self.persist_path = persist_path
        self.observations: deque = deque(maxlen=max_history)
        self.session_start = datetime.now().isoformat()
        
        # Load persisted memory if available
        if persist_path and persist_path.exists():
            self._load_from_disk()
    
    def record(self, user_input: str, goal: Optional[str], confidence: float,
               app_name: Optional[str], success: bool, message: str) -> None:
        """
        Record a new observation.
        
        Args:
            user_input: Raw user input
            goal: Interpreted goal
            confidence: Confidence score
            app_name: Selected application name
            success: Whether execution succeeded
            message: Result message
        """
        observation = Observation(
            timestamp=datetime.now().isoformat(),
            user_input=user_input,
            goal=goal,
            confidence=confidence,
            app_name=app_name,
            success=success,
            message=message
        )
        
        self.observations.append(observation)
        logger.info(f"Recorded observation: {observation.user_input} -> {observation.app_name}")
        
        # Persist if path is set
        if self.persist_path:
            self._save_to_disk()
    
    def get_recent(self, count: int = 10) -> List[Dict[str, Any]]:
        """
        Get recent observations.
        
        Args:
            count: Number of recent observations to retrieve
            
        Returns:
            List of observation dictionaries
        """
        recent = list(self.observations)[-count:]
        return [obs.to_dict() for obs in recent]
    
    def get_successful_launches(self) -> List[str]:
        """
        Get list of successfully launched apps.
        
        Returns:
            List of app names that were successfully launched
        """
        successful = [
            obs.app_name 
            for obs in self.observations 
            if obs.success and obs.app_name
        ]
        return successful
    
    def get_failed_attempts(self) -> List[Dict[str, Any]]:
        """
        Get list of failed attempts.
        
        Returns:
            List of observations where execution failed
        """
        failed = [
            obs.to_dict() 
            for obs in self.observations 
            if not obs.success
        ]
        return failed
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get memory statistics.
        
        Returns:
            Dictionary with memory stats
        """
        total = len(self.observations)
        successful = sum(1 for obs in self.observations if obs.success)
        failed = total - successful
        
        # Calculate average confidence
        avg_confidence = 0.0
        if total > 0:
            avg_confidence = sum(obs.confidence for obs in self.observations) / total
        
        # Get most common apps
        app_counts = {}
        for obs in self.observations:
            if obs.app_name:
                app_counts[obs.app_name] = app_counts.get(obs.app_name, 0) + 1
        
        most_used = sorted(app_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            'session_start': self.session_start,
            'total_interactions': total,
            'successful': successful,
            'failed': failed,
            'success_rate': successful / total if total > 0 else 0.0,
            'average_confidence': avg_confidence,
            'most_used_apps': dict(most_used),
            'memory_size': len(self.observations),
            'max_history': self.max_history
        }
    
    def clear(self) -> None:
        """Clear all observations from memory."""
        self.observations.clear()
        logger.info("Memory cleared")
        
        if self.persist_path:
            self._save_to_disk()
    
    def _save_to_disk(self) -> None:
        """Persist memory to disk."""
        if not self.persist_path:
            return
        
        try:
            # Create parent directory if needed
            self.persist_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Prepare data
            data = {
                'session_start': self.session_start,
                'observations': [obs.to_dict() for obs in self.observations]
            }
            
            # Write to disk
            with open(self.persist_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.debug(f"Memory persisted to: {self.persist_path}")
            
        except Exception as e:
            logger.error(f"Failed to persist memory: {e}")
    
    def _load_from_disk(self) -> None:
        """Load memory from disk."""
        if not self.persist_path or not self.persist_path.exists():
            return
        
        try:
            with open(self.persist_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Restore session start
            self.session_start = data.get('session_start', self.session_start)
            
            # Restore observations
            for obs_dict in data.get('observations', []):
                obs = Observation(**obs_dict)
                self.observations.append(obs)
            
            logger.info(f"Loaded {len(self.observations)} observations from disk")
            
        except Exception as e:
            logger.error(f"Failed to load memory: {e}")


# Example usage and testing
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "=" * 60)
    print("AGENT MEMORY TEST")
    print("=" * 60)
    
    # Create memory instance
    memory = AgentMemory(max_history=5)
    
    # Record some observations
    test_interactions = [
        ("open notepad", "write_text", 0.9, "notepad", True, "Success"),
        ("launch chrome", "launch_chrome", 0.95, "chrome", True, "Success"),
        ("start vscode", "code", 0.85, "vscode", True, "Success"),
        ("delete files", None, 0.3, None, False, "Low confidence"),
        ("open firefox", "browse_web", 0.9, "firefox", True, "Success"),
        ("run photoshop", "design", 0.8, None, False, "App not found"),
    ]
    
    for user_input, goal, conf, app, success, msg in test_interactions:
        memory.record(user_input, goal, conf, app, success, msg)
    
    # Display stats
    print("\nMemory Stats:")
    stats = memory.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Display recent observations
    print("\nRecent Observations:")
    for obs in memory.get_recent(3):
        print(f"  {obs['user_input']} -> {obs['app_name']} ({obs['success']})")
    
    # Display successful launches
    print("\nSuccessful Launches:")
    for app in memory.get_successful_launches():
        print(f"  - {app}")
