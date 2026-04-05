# AI Desktop Agent - Documentation Index

## 📚 Documentation Overview

This project contains comprehensive documentation for the AI Desktop Agent - a security-first Windows application launcher that uses natural language processing.

## 🚀 Getting Started

**New to this project?** Start here:

1. **[QUICKSTART.md](QUICKSTART.md)** - Get up and running in 5 minutes
   - Installation instructions
   - First-time setup
   - Usage examples
   - Common issues and solutions

2. **[README.md](README.md)** - Complete project overview
   - Security philosophy
   - Architecture overview
   - Features and capabilities
   - Threat model
   - FAQ

## 📖 Documentation Files

### Core Documentation

| Document | Purpose | Audience |
|----------|---------|----------|
| **[QUICKSTART.md](QUICKSTART.md)** | Quick setup and usage guide | All users |
| **[README.md](README.md)** | Comprehensive project overview | All users |
| **[ARCHITECTURE.md](ARCHITECTURE.md)** | Technical architecture details | Developers |
| **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** | Refactoring summary and metrics | Project stakeholders |

### Quick Reference

- **Want to use the agent?** → [QUICKSTART.md](QUICKSTART.md)
- **Want to understand the security model?** → [README.md](README.md#-security-features)
- **Want to extend the system?** → [ARCHITECTURE.md](ARCHITECTURE.md#extension-points)
- **Want to see what was built?** → [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

## 🏗️ Project Structure

```
echo-desk/
├── 📄 Documentation
│   ├── INDEX.md              ← You are here
│   ├── QUICKSTART.md         ← Start here for usage
│   ├── README.md             ← Full project overview
│   ├── ARCHITECTURE.md       ← Technical deep dive
│   └── PROJECT_SUMMARY.md    ← What was built
│
├── 🔧 Phase 1: Bootstrap (One-Time Discovery)
│   └── tools/
│       ├── __init__.py
│       └── bootstrap_scan.py  ← Discovers installed apps
│
├── 🤖 Phase 2: AI Agent Runtime
│   ├── main.py               ← Primary entry point & orchestrator
│   ├── main_chat.py          ← Optional: conversational agent
│   │
│   ├── llm/                  ← Natural language processing
│   │   ├── __init__.py
│   │   └── interpreter.py    ← Text → Structured goals
│   │
│   ├── policy/               ← Decision making
│   │   ├── __init__.py
│   │   └── decision.py       ← Goal → App name mapping
│   │
│   ├── system/               ← Safe execution
│   │   ├── __init__.py
│   │   └── executor.py       ← Launches apps safely
│   │
│   ├── memory/               ← State management
│   │   ├── __init__.py
│   │   └── state.py          ← Tracks observations
│   │
│   └── ui/                   ← User interface
│       ├── __init__.py
│       └── cli.py            ← Command-line interface
│
├── 📊 Data & Configuration
│   └── config/
│       ├── __init__.py
│       ├── app_registry.json ← Whitelist (generated)
│       └── memory.json       ← Agent memory (auto-created)
│
└── 🔒 Security
    └── .gitignore            ← Excludes sensitive files
```

## 🎯 Common Tasks

### For Users

| Task | Documentation | Command |
|------|---------------|---------|
| First-time setup | [QUICKSTART.md](QUICKSTART.md#first-time-setup) | `python -m tools.bootstrap_scan` |
| Run the agent | [QUICKSTART.md](QUICKSTART.md#step-2-run-the-agent) | `python main.py` |
| Conversational / chat mode | [QUICKSTART.md](QUICKSTART.md#entry-points) | `python main_chat.py` |
| Test without launching apps | [QUICKSTART.md](QUICKSTART.md#testing-dry-run-mode) | `python main.py --dry-run` |
| List available apps | [QUICKSTART.md](QUICKSTART.md#list-available-apps) | Type `list` in agent |
| View statistics | [QUICKSTART.md](QUICKSTART.md#view-statistics) | Type `stats` in agent |
| Refresh app list | [QUICKSTART.md](QUICKSTART.md#refresh-application-registry) | `python -m tools.bootstrap_scan` |

### For Developers

| Task | Documentation | Location |
|------|---------------|----------|
| Understand architecture | [ARCHITECTURE.md](ARCHITECTURE.md) | Full document |
| Add new applications | [ARCHITECTURE.md](ARCHITECTURE.md#adding-new-applications) | `config/app_registry.json` |
| Add intent patterns | [ARCHITECTURE.md](ARCHITECTURE.md#adding-new-intent-patterns) | `llm/interpreter.py` |
| Add policy mappings | [ARCHITECTURE.md](ARCHITECTURE.md#adding-new-policy-mappings) | `policy/decision.py` |
| Adjust confidence | [ARCHITECTURE.md](ARCHITECTURE.md#confidence-threshold) | `main.py` |
| Integrate real LLM | [ARCHITECTURE.md](ARCHITECTURE.md#integrating-real-llm) | `llm/interpreter.py` |

### For Security Reviewers

| Topic | Documentation | Section |
|-------|---------------|---------|
| Security philosophy | [README.md](README.md#-security-philosophy-the-binary-boundary) | Binary Boundary |
| Security features | [README.md](README.md#-security-features) | Full section |
| Threat model | [README.md](README.md#-threat-model) | What prevents/doesn't prevent |
| Security layers | [ARCHITECTURE.md](ARCHITECTURE.md#security-layers) | 6 layers explained |
| Module contracts | [ARCHITECTURE.md](ARCHITECTURE.md#module-contracts) | Security constraints |

## 🔐 Security Model

The system implements a **Binary Boundary** between two phases:

### Phase 1: Bootstrap (Deterministic)
- **File**: `tools/bootstrap_scan.py`
- **Purpose**: One-time application discovery
- **Security**: NO LLM, NO execution, NO network
- **Output**: `config/app_registry.json` (read-only whitelist)

### Phase 2: AI Agent (Runtime)
- **File**: `main.py` (primary orchestrator); optional `main_chat.py` for conversational mode
- **Purpose**: Natural language application launching
- **Security**: LLM never sees paths, executor uses `shell=False`
- **Input**: Natural language text ONLY

**Key Principle**: The LLM interprets intent but NEVER sees file paths or commands. The executor receives ONLY validated paths from the whitelist.

## 📊 Project Metrics

| Metric | Value |
|--------|-------|
| **Total Files Created** | 20+ |
| **Lines of Code** | ~3,000 |
| **Security Layers** | 6 |
| **Applications Discovered** | 1,025 |
| **Documentation Pages** | 5 |
| **Modules** | 7 |

## 🎓 Key Concepts

### The Binary Boundary
The strict separation between application discovery (Phase 1) and execution (Phase 2). This prevents the agent from discovering or executing arbitrary files at runtime.

### Security by Design
Every module is designed with security constraints:
- LLM: NEVER sees paths
- Policy: NEVER constructs paths
- Executor: NEVER uses shell=True
- Registry: Read-only at runtime

### Defense in Depth
6 layers of security validation:
1. Input validation
2. LLM interpretation
3. Policy mapping
4. Registry validation
5. Path validation
6. Safe execution

### Fail-Safe
Unknown or low-confidence input results in safe failure, not execution.

## 🔄 Workflow

### First-Time Setup
```
1. Read QUICKSTART.md
2. Run: python -m tools.bootstrap_scan
3. Review: config/app_registry.json
4. Run: python main.py --dry-run
5. Test with real apps: python main.py
```

### Daily Usage
```
1. Run: python main.py (or python main_chat.py for conversational mode)
2. Type natural language commands
3. Type 'help' for assistance
4. Type 'list' to see apps
5. Type 'stats' to see usage
6. Type 'exit' to quit
```

### Development Workflow
```
1. Read ARCHITECTURE.md
2. Modify modules as needed
3. Test individual modules
4. Test with --dry-run
5. Test with real execution
6. Review agent.log
```

## 🐛 Troubleshooting

| Issue | Solution | Documentation |
|-------|----------|---------------|
| "Registry not found" | Run bootstrap scan | [QUICKSTART.md](QUICKSTART.md#issue-application-registry-not-found) |
| "App not found" | Check if app is in registry | [QUICKSTART.md](QUICKSTART.md#issue-app-notepad-not-found-in-registry) |
| "Low confidence" | Be more specific | [QUICKSTART.md](QUICKSTART.md#issue-could-not-understand-your-request) |
| System apps missing | Add to scan paths | [README.md](README.md#-configuration) |

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| **1.0.0** | 2026-02-07 | Initial release with security-first architecture |

## 🤝 Contributing

When contributing, please:
1. Read [ARCHITECTURE.md](ARCHITECTURE.md) to understand the design
2. Maintain the security constraints
3. Never allow LLM to see paths
4. Never use `shell=True`
5. Always validate against registry
6. Update documentation

## 📞 Support

For questions or issues:
1. Check [QUICKSTART.md](QUICKSTART.md) for common issues
2. Review [README.md](README.md) FAQ section
3. Examine [ARCHITECTURE.md](ARCHITECTURE.md) for technical details
4. Check `agent.log` for error messages

## 🎯 Next Steps

**Just starting?**
→ Go to [QUICKSTART.md](QUICKSTART.md)

**Want to understand the system?**
→ Go to [README.md](README.md)

**Need technical details?**
→ Go to [ARCHITECTURE.md](ARCHITECTURE.md)

**Want to see what was built?**
→ Go to [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

---

**Built with Security by Design** 🔒

*Last Updated: February 7, 2026*
