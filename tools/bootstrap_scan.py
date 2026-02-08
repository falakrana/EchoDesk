"""
Phase 1: Bootstrap Application Discovery (NO LLM)

This module performs a ONE-TIME, deterministic scan of the Windows system
to discover installed applications. It NEVER executes any found files and
NEVER uses LLM for decision-making.

SECURITY CONSTRAINTS:
- Purely deterministic logic
- No LLM calls
- No execution of discovered files
- No network requests
- Read-only file system operations only

OUTPUT: config/app_registry.json
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Set
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class BootstrapScanner:
    """
    Deterministic application discovery scanner.
    
    This class scans standard Windows directories for executable files,
    filters out system utilities and installers, and generates a normalized
    registry of user-facing applications.
    """
    
    # Standard Windows application directories
    SCAN_PATHS = [
        Path(os.environ.get('ProgramFiles', 'C:\\Program Files')),
        Path(os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')),
        Path(os.environ.get('LOCALAPPDATA', '')).joinpath('Programs') if os.environ.get('LOCALAPPDATA') else None,
    ]
    
    # Patterns to EXCLUDE (installers, updaters, uninstallers, background helpers)
    EXCLUDE_PATTERNS = [
        r'unins\d+\.exe$',  # Uninstallers
        r'uninstall.*\.exe$',
        r'uninst\.exe$',
        r'update.*\.exe$',  # Updaters
        r'.*updater\.exe$',
        r'setup.*\.exe$',  # Installers
        r'install.*\.exe$',
        r'.*installer\.exe$',
        r'vcredist.*\.exe$',  # Redistributables
        r'.*_is\d+\.exe$',  # InstallShield
        r'helper\.exe$',  # Background helpers
        r'.*service\.exe$',
        r'.*daemon\.exe$',
        r'crash.*reporter\.exe$',  # Crash reporters
        r'feedback.*\.exe$',
    ]
    
    def __init__(self):
        """Initialize the scanner."""
        self.discovered_apps: Dict[str, str] = {}
        self.excluded_count = 0
        
    def _should_exclude(self, exe_name: str) -> bool:
        """
        Check if an executable should be excluded based on patterns.
        
        Args:
            exe_name: Name of the executable file
            
        Returns:
            True if the file should be excluded, False otherwise
        """
        exe_lower = exe_name.lower()
        
        for pattern in self.EXCLUDE_PATTERNS:
            if re.search(pattern, exe_lower, re.IGNORECASE):
                return True
        
        return False
    
    def _normalize_app_name(self, exe_path: Path) -> str:
        """
        Create a user-friendly key from an executable path.
        
        Examples:
            "Code.exe" -> "vscode"
            "chrome.exe" -> "chrome"
            "Microsoft Edge.exe" -> "edge"
            
        Args:
            exe_path: Path to the executable
            
        Returns:
            Normalized application name (lowercase, no extension)
        """
        exe_name = exe_path.stem.lower()
        
        # Special case mappings for common applications
        special_mappings = {
            'code': 'vscode',
            'msedge': 'edge',
            'firefox': 'firefox',
            'chrome': 'chrome',
            'notepad++': 'notepadplusplus',
            'winword': 'word',
            'excel': 'excel',
            'powerpnt': 'powerpoint',
            'outlook': 'outlook',
            'teams': 'teams',
            'slack': 'slack',
            'discord': 'discord',
            'spotify': 'spotify',
            'vlc': 'vlc',
            'gimp': 'gimp',
            'inkscape': 'inkscape',
            'blender': 'blender',
            'obs64': 'obs',
            'obs32': 'obs',
        }
        
        # Return special mapping if exists, otherwise return normalized name
        return special_mappings.get(exe_name, exe_name)
    
    def _scan_directory(self, directory: Path) -> None:
        """
        Recursively scan a directory for executable files.
        
        Args:
            directory: Directory path to scan
        """
        if not directory or not directory.exists():
            logger.warning(f"Directory does not exist: {directory}")
            return
        
        logger.info(f"Scanning: {directory}")
        
        try:
            # Walk through directory tree
            for root, dirs, files in os.walk(directory):
                # Skip certain directories for performance
                dirs[:] = [d for d in dirs if d.lower() not in ['__pycache__', 'node_modules', '.git']]
                
                for file in files:
                    if file.lower().endswith('.exe'):
                        exe_path = Path(root) / file
                        
                        # Check exclusion patterns
                        if self._should_exclude(file):
                            self.excluded_count += 1
                            logger.debug(f"Excluded: {file}")
                            continue
                        
                        # Normalize and store
                        app_key = self._normalize_app_name(exe_path)
                        
                        # Avoid duplicates (keep first occurrence)
                        if app_key not in self.discovered_apps:
                            self.discovered_apps[app_key] = str(exe_path)
                            logger.info(f"Discovered: {app_key} -> {exe_path}")
                        
        except PermissionError as e:
            logger.warning(f"Permission denied: {directory} - {e}")
        except Exception as e:
            logger.error(f"Error scanning {directory}: {e}")
    
    def scan_system(self) -> Dict[str, str]:
        """
        Perform a complete system scan for applications.
        
        Returns:
            Dictionary mapping app names to executable paths
        """
        logger.info("=" * 60)
        logger.info("PHASE 1: BOOTSTRAP APPLICATION DISCOVERY")
        logger.info("=" * 60)
        
        # Scan all configured paths
        for scan_path in self.SCAN_PATHS:
            if scan_path:
                self._scan_directory(scan_path)
        
        logger.info("=" * 60)
        logger.info(f"Scan complete!")
        logger.info(f"  Discovered: {len(self.discovered_apps)} applications")
        logger.info(f"  Excluded: {self.excluded_count} files")
        logger.info("=" * 60)
        
        return self.discovered_apps
    
    def save_registry(self, output_path: Path) -> None:
        """
        Save the discovered applications to a JSON registry file.
        
        Args:
            output_path: Path to save the registry JSON file
        """
        registry_data = {
            "version": "1.0.0",
            "generated_at": None,  # Will be set at runtime
            "scan_paths": [str(p) for p in self.SCAN_PATHS if p],
            "total_apps": len(self.discovered_apps),
            "applications": self.discovered_apps
        }
        
        # Create parent directory if it doesn't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write JSON with pretty formatting
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(registry_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Registry saved to: {output_path}")


def main():
    """
    Main entry point for bootstrap scanning.
    
    This function should be run ONCE during initial setup or when
    the user wants to refresh the application registry.
    """
    import datetime
    
    # Determine output path
    script_dir = Path(__file__).parent.parent
    output_path = script_dir / 'config' / 'app_registry.json'
    
    # Create scanner and perform discovery
    scanner = BootstrapScanner()
    apps = scanner.scan_system()
    
    # Add timestamp before saving
    scanner.discovered_apps = apps
    scanner.save_registry(output_path)
    
    print("\n" + "=" * 60)
    print("✓ Bootstrap scan complete!")
    print(f"✓ Registry saved: {output_path}")
    print(f"✓ Total applications: {len(apps)}")
    print("=" * 60)
    print("\nYou can now run the AI agent with: python main.py")


if __name__ == '__main__':
    main()
