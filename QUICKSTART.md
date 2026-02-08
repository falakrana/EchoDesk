# Quick Start Guide

## Installation

No installation required! The project uses only Python standard library.

**Requirements**:
- Python 3.7+
- Windows OS

## First Time Setup

### Step 1: Run Bootstrap Scan

This discovers all installed applications on your system:

```powershell
cd ai_desktop_agent
python -m tools.bootstrap_scan
```

**Expected Output**:
```
============================================================
PHASE 1: BOOTSTRAP APPLICATION DISCOVERY
============================================================
INFO: Scanning: C:\Program Files
INFO: Discovered: chrome -> C:\Program Files\Google\Chrome\...
INFO: Discovered: vscode -> C:\Users\...\Code.exe
...
============================================================
Scan complete!
  Discovered: 1000+ applications
  Excluded: 200+ files
============================================================

✓ Bootstrap scan complete!
✓ Registry saved: config\app_registry.json
✓ Total applications: 1025
```

### Step 2: Run the Agent

```powershell
python main.py
```

**Expected Output**:
```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           AI DESKTOP AGENT - Security-First Edition         ║
║                                                              ║
║  Natural Language Application Launcher for Windows          ║
║  Built with Safety by Design                                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

ℹ Loaded 1025 applications
ℹ Type 'help' for commands or describe what you want to do

>
```

## Usage Examples

### Launch an Application

```
> open chrome
  Goal: launch_chrome (confidence: 95%)
✓ Successfully launched: chrome.exe
```

### Use Natural Language

```
> I want to write code
  Goal: code (confidence: 85%)
✓ Successfully launched: Code.exe
```

### List Available Apps

```
> list
Available Applications:
============================================================
    1. 7zr
    2. aws
    3. brave
    4. chrome
    5. docker
    ...
  1025. zucchini
============================================================
Total: 1025 applications
```

### View Statistics

```
> stats
Agent Statistics:
============================================================
  Session Start: 2026-02-07T12:00:00
  Total Interactions: 5
  Successful: 4
  Failed: 1
  Success Rate: 80.0%
  Average Confidence: 87.5%

  Most Used Apps:
    - chrome: 2 times
    - vscode: 1 times
============================================================
```

### Get Help

```
> help
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
```

## Testing (Dry Run Mode)

Test the agent without actually launching applications:

```powershell
python main.py --dry-run
```

This will simulate execution and show what would happen without actually launching apps.

## Common Issues

### Issue: "Application registry not found!"

**Solution**: Run the bootstrap scan first:
```powershell
python -m tools.bootstrap_scan
```

### Issue: "App 'notepad' not found in registry"

**Cause**: System utilities (like notepad) are in `C:\Windows\System32` which isn't scanned by default.

**Solution**: Either:
1. Manually add to `config/app_registry.json`:
   ```json
   {
     "applications": {
       "notepad": "C:\\Windows\\System32\\notepad.exe"
     }
   }
   ```

2. Or modify `tools/bootstrap_scan.py` to include `C:\Windows\System32` and re-run the scan.

### Issue: "Could not understand your request"

**Cause**: Low confidence interpretation (below 70%).

**Solution**: Be more specific:
- ❌ "I need something"
- ✅ "I want to open chrome"
- ✅ "launch vscode"

## Tips

1. **Be Specific**: Use action verbs like "open", "launch", "start"
2. **Use App Names**: Mention the app name directly for best results
3. **Check the List**: Use `list` to see all available apps
4. **Review Stats**: Use `stats` to see your usage patterns
5. **Dry Run First**: Test with `--dry-run` before actual use

## Advanced

### Refresh Application Registry

If you install new applications, refresh the registry:

```powershell
python -m tools.bootstrap_scan
```

This will re-scan and update `config/app_registry.json`.

### Clear Memory

```
> clear
⚠ Clear all memory? (y/n): y
✓ Memory cleared
```

### Adjust Confidence Threshold

Edit `main.py`:
```python
class AIDesktopAgent:
    MIN_CONFIDENCE = 0.70  # Change this (0.0 to 1.0)
```

Lower = more permissive, Higher = more strict

## Exit

```
> exit

Goodbye! 👋

Agent Statistics:
============================================================
  Session Start: 2026-02-07T12:00:00
  Total Interactions: 10
  Successful: 9
  Failed: 1
  Success Rate: 90.0%
============================================================
```

---

**Ready to go!** 🚀

For more details, see [README.md](README.md)
