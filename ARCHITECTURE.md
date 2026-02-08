# ARCHITECTURE DOCUMENTATION

## System Overview

The AI Desktop Agent is built on a **security-first architecture** that fundamentally separates application discovery from execution through a concept called the **Binary Boundary**.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        AI DESKTOP AGENT SYSTEM                          │
│                     Security-First Architecture                         │
└─────────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────┐         ┌──────────────────────────────┐
│   PHASE 1: BOOTSTRAP         │         │   PHASE 2: AI AGENT          │
│   (One-Time Discovery)       │         │   (Runtime Execution)        │
└──────────────────────────────┘         └──────────────────────────────┘

┌──────────────────────────────┐         ┌──────────────────────────────┐
│  tools/bootstrap_scan.py     │         │  User Input                  │
│  ┌────────────────────────┐  │         │  "I want to write code"      │
│  │ Deterministic Scanner  │  │         └──────────┬───────────────────┘
│  │ - NO LLM               │  │                    │
│  │ - NO Execution         │  │                    ▼
│  │ - NO Network           │  │         ┌──────────────────────────────┐
│  └────────────────────────┘  │         │  llm/interpreter.py          │
│             │                 │         │  ┌────────────────────────┐  │
│             ▼                 │         │  │ Natural Language → Goal│  │
│  ┌────────────────────────┐  │         │  │ NEVER sees paths       │  │
│  │ Windows File System    │  │         │  └────────────────────────┘  │
│  │ - Program Files        │  │         └──────────┬───────────────────┘
│  │ - Program Files (x86)  │  │                    │
│  │ - AppData\Local\...    │  │                    ▼
│  └────────────────────────┘  │         ┌──────────────────────────────┐
│             │                 │         │  policy/decision.py          │
│             ▼                 │         │  ┌────────────────────────┐  │
│  ┌────────────────────────┐  │         │  │ Goal → App Name        │  │
│  │ Filtering & Exclusion  │  │         │  │ Policy-based mapping   │  │
│  │ - Uninstallers         │  │         │  └────────────────────────┘  │
│  │ - Updaters             │  │         └──────────┬───────────────────┘
│  │ - Installers           │  │                    │
│  └────────────────────────┘  │                    ▼
│             │                 │         ┌──────────────────────────────┐
│             ▼                 │         │  Registry Validator          │
│  ┌────────────────────────┐  │    ┌───▶│  (main.py)                   │
│  │ Normalization          │  │    │    │  ┌────────────────────────┐  │
│  │ - code.exe → vscode    │  │    │    │  │ App Name → Path        │  │
│  │ - chrome.exe → chrome  │  │    │    │  │ Checks whitelist       │  │
│  └────────────────────────┘  │    │    │  └────────────────────────┘  │
│             │                 │    │    └──────────┬───────────────────┘
│             ▼                 │    │               │
│  ┌────────────────────────┐  │    │               ▼
│  │ config/                │  │    │    ┌──────────────────────────────┐
│  │ app_registry.json      │◀─┼────┘    │  system/executor.py          │
│  │                        │  │         │  ┌────────────────────────┐  │
│  │ {                      │  │         │  │ Safe Execution         │  │
│  │   "vscode": "C:\...",  │  │         │  │ - shell=False          │  │
│  │   "chrome": "C:\...",  │  │         │  │ - List form only       │  │
│  │   ...                  │  │         │  │ - No dynamic args      │  │
│  │ }                      │  │         │  └────────────────────────┘  │
│  │                        │  │         └──────────┬───────────────────┘
│  │ READ-ONLY WHITELIST    │  │                    │
│  └────────────────────────┘  │                    ▼
│                               │         ┌──────────────────────────────┐
│  ✓ 1025 apps discovered       │         │  Application Launches        │
│  ✓ Installers excluded        │         │  ✓ Success                   │
│  ✓ JSON generated             │         └──────────────────────────────┘
└──────────────────────────────┘                    │
                                                    ▼
                                         ┌──────────────────────────────┐
                                         │  memory/state.py             │
                                         │  ┌────────────────────────┐  │
                                         │  │ Record Observation     │  │
                                         │  │ - User input           │  │
                                         │  │ - Goal extracted       │  │
                                         │  │ - App launched         │  │
                                         │  │ - Success/failure      │  │
                                         │  └────────────────────────┘  │
                                         └──────────────────────────────┘

═══════════════════════════════════════════════════════════════════════════
                           THE BINARY BOUNDARY
═══════════════════════════════════════════════════════════════════════════

PHASE 1 (Bootstrap)              │              PHASE 2 (Runtime)
─────────────────────────────────┼─────────────────────────────────────────
• Runs ONCE during setup         │  • Runs every time agent starts
• Deterministic logic only       │  • Uses LLM for interpretation
• Scans file system              │  • NEVER scans file system
• Generates whitelist            │  • ONLY reads whitelist
• NO execution                   │  • Executes whitelisted apps
• NO LLM                         │  • LLM isolated from paths
─────────────────────────────────┴─────────────────────────────────────────
```

## Security Layers

### Layer 1: Input Validation (main.py)
```
User Input → Check empty → Check special commands → Pass to LLM
```

### Layer 2: LLM Interpretation (llm/interpreter.py)
```
Raw Text → Extract Goal → Calculate Confidence → Return Structured JSON

Input:  "I want to write code"
Output: {"goal": "code", "confidence": 0.85}

CRITICAL: LLM NEVER sees:
  ✗ File paths
  ✗ Executable names
  ✗ System commands
  ✗ Registry contents
```

### Layer 3: Policy Mapping (policy/decision.py)
```
Goal → Lookup Policy → Select App Name → Return App Name

Input:  "code"
Policy: {"code": ["vscode", "sublime", "atom", ...]}
Output: "vscode"

CRITICAL: Policy engine NEVER:
  ✗ Constructs file paths
  ✗ Executes anything
  ✗ Sees user input directly
```

### Layer 4: Registry Validation (main.py)
```
App Name → Check Whitelist → Return Path or None

Input:  "vscode"
Registry: {"vscode": "C:\\Users\\...\\Code.exe"}
Output: "C:\\Users\\...\\Code.exe"

CRITICAL: Registry is:
  ✓ Read-only during runtime
  ✓ Generated by Phase 1 only
  ✓ Never modified by agent
```

### Layer 5: Path Validation (system/executor.py)
```
Path → Check exists → Check is file → Check is .exe → Check absolute
```

### Layer 6: Safe Execution (system/executor.py)
```python
# SAFE: List form, shell=False
subprocess.Popen([path], shell=False)

# NEVER USED: String form, shell=True
subprocess.Popen(path, shell=True)  # ✗ FORBIDDEN
```

## Data Flow

### Successful Execution Flow
```
1. User: "open chrome"
2. CLI: Captures input
3. Main: Receives "open chrome"
4. LLM: Extracts goal="launch_chrome", confidence=0.95
5. Policy: Maps "launch_chrome" → "chrome"
6. Registry: Validates "chrome" → "C:\\Program Files\\Google\\Chrome\\...\\chrome.exe"
7. Executor: Validates path → Launches with subprocess
8. Memory: Records observation
9. CLI: Shows "✓ Successfully launched: chrome.exe"
```

### Failed Execution Flow (Low Confidence)
```
1. User: "I need something"
2. CLI: Captures input
3. Main: Receives "I need something"
4. LLM: Extracts goal=None, confidence=0.3
5. Main: Confidence < 0.70 → REJECT
6. Memory: Records failure
7. CLI: Shows "✗ Could not understand your request"
```

### Failed Execution Flow (Not in Registry)
```
1. User: "open photoshop"
2. CLI: Captures input
3. Main: Receives "open photoshop"
4. LLM: Extracts goal="launch_photoshop", confidence=0.95
5. Policy: Maps "launch_photoshop" → "photoshop"
6. Registry: Checks "photoshop" → NOT FOUND
7. Memory: Records failure
8. CLI: Shows "✗ Application 'photoshop' not found in registry"
```

## Module Contracts

### tools/bootstrap_scan.py
**Input**: None (scans file system)
**Output**: `config/app_registry.json`
**Constraints**:
- MUST NOT use LLM
- MUST NOT execute discovered files
- MUST filter out installers/updaters
- MUST normalize app names
- MUST generate valid JSON

### llm/interpreter.py
**Input**: Raw natural language string
**Output**: `{"goal": str, "confidence": float, "raw_input": str}`
**Constraints**:
- MUST NOT see file paths
- MUST NOT see executable names
- MUST NOT see registry contents
- MUST return confidence between 0.0 and 1.0
- MUST return None for unrecognized input

### policy/decision.py
**Input**: Structured goal string (e.g., "code", "launch_chrome")
**Output**: App name string (e.g., "vscode", "chrome") or None
**Constraints**:
- MUST NOT construct file paths
- MUST NOT execute anything
- MUST use predefined policy mappings
- MUST validate against registry if available

### system/executor.py
**Input**: Validated executable path (absolute path string)
**Output**: `{"success": bool, "message": str, "path": str}`
**Constraints**:
- MUST validate path before execution
- MUST use `subprocess.Popen([path], shell=False)`
- MUST NEVER use `shell=True`
- MUST NEVER accept dynamic arguments
- MUST check file exists and is .exe

### memory/state.py
**Input**: Observation data (user_input, goal, app_name, success, message)
**Output**: None (stores in memory)
**Constraints**:
- MUST persist to disk
- MUST track statistics
- MUST limit history size
- MUST NOT store sensitive paths in plain text

### ui/cli.py
**Input**: Various data for display
**Output**: Terminal output
**Constraints**:
- MUST NOT contain business logic
- MUST NOT make system calls
- MUST NOT access file system
- MUST only display and collect input

## Configuration

### Confidence Threshold
```python
# main.py
class AIDesktopAgent:
    MIN_CONFIDENCE = 0.70  # Adjustable (0.0 to 1.0)
```

### Scan Paths
```python
# tools/bootstrap_scan.py
SCAN_PATHS = [
    Path(os.environ.get('ProgramFiles')),
    Path(os.environ.get('ProgramFiles(x86)')),
    Path(os.environ.get('LOCALAPPDATA')).joinpath('Programs'),
    # Add more paths as needed
]
```

### Exclusion Patterns
```python
# tools/bootstrap_scan.py
EXCLUDE_PATTERNS = [
    r'unins\d+\.exe$',
    r'update.*\.exe$',
    r'setup.*\.exe$',
    # Add more patterns as needed
]
```

### Policy Mappings
```python
# policy/decision.py
GOAL_TO_APP_POLICY = {
    'write_text': ['notepad', 'notepadplusplus', 'vscode'],
    'code': ['vscode', 'sublime', 'atom'],
    # Add more mappings as needed
}
```

## Extension Points

### Adding New Applications
1. Run bootstrap scan: `python -m tools.bootstrap_scan`
2. Or manually edit `config/app_registry.json`

### Adding New Intent Patterns
Edit `llm/interpreter.py`:
```python
INTENT_PATTERNS = {
    'your_goal': [
        r'your regex pattern',
    ],
}
```

### Adding New Policy Mappings
Edit `policy/decision.py`:
```python
GOAL_TO_APP_POLICY = {
    'your_goal': ['app1', 'app2', 'app3'],
}
```

### Integrating Real LLM
Replace rule-based logic in `llm/interpreter.py`:
```python
def interpret(self, user_input: str) -> Dict[str, any]:
    # Call your LLM API here
    # Return structured JSON
    pass
```

## Testing Strategy

### Unit Testing
Each module can be tested independently:
```powershell
python -m tools.bootstrap_scan
python -m llm.interpreter
python -m policy.decision
python -m system.executor
python -m memory.state
python -m ui.cli
```

### Integration Testing
```powershell
# Dry run mode (no actual execution)
python main.py --dry-run
```

### Manual Testing
```powershell
# Full agent with real execution
python main.py
```

## Deployment

### Production Checklist
- [ ] Review `config/app_registry.json`
- [ ] Test in dry-run mode
- [ ] Verify confidence threshold
- [ ] Check policy mappings
- [ ] Review exclusion patterns
- [ ] Test with real applications
- [ ] Monitor `agent.log`
- [ ] Set up memory persistence

### Security Checklist
- [ ] Registry is read-only
- [ ] LLM never sees paths
- [ ] Executor uses shell=False
- [ ] No dynamic arguments
- [ ] Confidence threshold set
- [ ] Exclusion patterns comprehensive
- [ ] Logging enabled

---

**Architecture Version**: 1.0.0  
**Last Updated**: February 7, 2026  
**Security Level**: High  
**Production Ready**: Yes (with review)
