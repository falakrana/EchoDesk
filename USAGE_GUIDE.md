# Step-by-Step Usage Guide

## 🎯 Your Goal
You want the AI Desktop Agent to understand natural language like **"I want to use brave"** and open the Brave browser.

## ✅ Current Status
- ✅ Dependencies installed (LangChain, Groq)
- ✅ Code updated with LLM integration
- ✅ Ready to configure and test

## 📋 Step-by-Step Instructions

### Step 1: Get Your Groq API Key (2 minutes)

1. **Open your browser** and go to:
   ```
   https://console.groq.com/keys
   ```

2. **Sign in**

3. **Create API Key**

4. **Copy the API key**

   ⚠️ **Important**: Keep this key secret! Don't share it publicly.

---

### Step 2: Create the `.env` File (1 minute)

1. **Open the folder**:
   ```
   c:\Users\Falak\Desktop\desktop-agent\ai_desktop_agent
   ```

2. **Create a new file** named exactly `.env` (no `.txt` extension!)

   **How to create `.env` file on Windows:**
   - Open Notepad
   - Type the content (see below)
   - Click "File" → "Save As"
   - In "File name", type: `.env` (with the quotes!)
   - In "Save as type", select "All Files"
   - Click "Save"

3. **Add this content** to the `.env` file:
   ```
   GROQ_API_KEY=paste_your_actual_api_key_here
   ```

4. **Save the file**

---

### Step 3: Verify Setup (1 minute)

Run this command to test if everything is configured correctly:

```bash
cd c:\Users\Falak\Desktop\desktop-agent\ai_desktop_agent
python llm/test_llm_interpreter.py
```

**What you should see:**
```
LLM INTERPRETER TEST - Groq Integration
================================================================
[1] Initializing LLM interpreter...
[2] Initializing rule-based interpreter...
...
```

If you see `WARNING - GROQ_API_KEY not set`, check your `.env` file.

---

### Step 4: Run the Agent (30 seconds)

```bash
python main.py
```

**You should see:**
```
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           AI DESKTOP AGENT - Security-First Edition         ║
║                                                              ║
║  Natural Language Application Launcher for Windows          ║
║  Built with Safety by Design                                ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

ℹ Loaded X applications
ℹ Type 'help' for commands or describe what you want to do

> 
```

---

### Step 5: Test It! (1 minute)

Try these commands:

**Test 1: Specific app**
```
> I want to use brave
  🤖 Goal: launch_brave (confidence: 95%)
  💭 Reasoning: User explicitly mentioned 'brave' browser
✓ Launching Brave Browser...
```

**Test 2: General intent**
```
> I need to browse the web
  🤖 Goal: browse_web (confidence: 90%)
  💭 Reasoning: User wants to browse the internet
✓ Launching Chrome...
```

**Test 3: Casual language**
```
> yo open notepad for me
  🤖 Goal: launch_notepad (confidence: 92%)
  💭 Reasoning: User wants to open notepad, casual language
✓ Launching Notepad...
```

---

## 🎉 Success!

If you see the 🤖 emoji and 💭 reasoning, the LLM is working!

---

## 🔧 Troubleshooting

### Problem: "GROQ_API_KEY not set"

**Solution:**
1. Check that `.env` file exists in `ai_desktop_agent` folder
2. Open `.env` and verify the API key is there
3. Make sure there are no quotes around the API key
4. Make sure the file is named exactly `.env` (not `.env.txt`)

**To check:**
```bash
cd c:\Users\Falak\Desktop\desktop-agent\ai_desktop_agent
type .env
```

You should see:
```
GROQ_API_KEY=abc_xyz_your_key_here
```

---

### Problem: "LangChain not available"

**Solution:**
```bash
cd c:\Users\Falak\Desktop\desktop-agent\ai_desktop_agent
python -m pip install -r requirements.txt
```

Wait for installation to complete, then try again.

---

### Problem: "Application 'brave' not found in registry"

**Solution:**
1. First, run the bootstrap scan to find installed applications:
   ```bash
   python -m tools.bootstrap_scan
   ```

2. Check if Brave is in the registry:
   ```bash
   python main.py
   > list
   ```

3. If Brave is not listed, you may need to add it manually to the registry or install Brave browser.

---

### Problem: Low confidence scores

**Solution:**
Be more specific in your input:
- ❌ "browser" → ✅ "open chrome"
- ❌ "text" → ✅ "launch notepad"
- ❌ "something to write" → ✅ "I want to write notes"

Use action verbs: open, launch, start, use

---

## 📚 Additional Resources

- **Quick Start**: [QUICKSTART_LLM.md](QUICKSTART_LLM.md)
- **Full Setup Guide**: [LLM_SETUP.md](LLM_SETUP.md)
- **Implementation Details**: [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
- **Architecture Diagram**: [ARCHITECTURE_DIAGRAM.txt](ARCHITECTURE_DIAGRAM.txt)

---

## 🎯 What You Can Do Now

### Supported Commands

**Specific Apps:**
- "I want to use brave"
- "open chrome"
- "launch notepad"
- "start visual studio code"
- "open spotify"

**General Intents:**
- "I need to browse the web"
- "I want to write notes"
- "I need to check my email"
- "open a text editor"

**Casual Language:**
- "yo open brave for me"
- "can u start notepad"
- "i wanna use firefox"

### Special Commands
- `help` - Show help
- `list` - List all available apps
- `stats` - Show statistics
- `exit` - Exit the agent

---

## 🚀 Next Steps

1. ✅ Get API key from Google AI Studio
2. ✅ Create `.env` file with your API key
3. ✅ Run test: `python llm/test_llm_interpreter.py`
4. ✅ Run agent: `python main.py`
5. ✅ Try: "I want to use brave"

---

## 💡 Tips for Best Results

1. **Be specific**: Mention app names when possible
2. **Use action verbs**: open, launch, start, use
3. **Keep it simple**: Short, clear commands work best
4. **Check the list**: Type `list` to see available apps

---

## 📞 Need Help?

Check the documentation:
- [QUICKSTART_LLM.md](QUICKSTART_LLM.md) - Quick setup
- [LLM_SETUP.md](LLM_SETUP.md) - Detailed guide
- [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) - Technical details

---

**Enjoy your LLM-powered desktop agent!** 🎉
