# Quick Start: LLM Integration

## 🚀 Get Started in 3 Steps

### Step 1: Get Your API Key
1. Go to the Groq Console: https://console.groq.com/keys
2. Sign in
3. Click **"Create API Key"**
4. Copy the API key

### Step 2: Create `.env` File
Create a file named `.env` in the project root (the `echo-desk` folder, next to `main.py`):

```bash
GROQ_API_KEY=paste_your_api_key_here
```

**Example:**
```bash
GROQ_API_KEY=gsk_8h3...
```

### Step 3: Run the Agent
```bash
python main.py
```

Optional conversational mode: `python main_chat.py` (see [QUICKSTART.md](QUICKSTART.md#entry-points)).

## 🧪 Test the LLM

Try these commands:
```
You: I want to use brave
You: open chrome
You: launch notepad
You: I need to browse the web
```

## 🔍 Test Script

Run the test script to see LLM in action:

```bash
# Automated tests
python llm/test_llm_interpreter.py

# Interactive mode
python llm/test_llm_interpreter.py --interactive
```

## ✅ Verify It's Working

When you run the agent, you should see the agent banner and loaded apps.

If you see this instead:
```
WARNING - GROQ_API_KEY not set
WARNING - Falling back to rule-based extraction
```

Then check:
1. `.env` file exists in the project root (same folder as `main.py`)
2. API key is correct (no quotes, no spaces)
3. File is named exactly `.env` (not `.env.txt`)

## 💡 Example Interaction

**With Groq:**
```
You: I want to use brave
🤖 Goal: launch_brave
📊 Confidence: 0.95
💭 Reasoning: User explicitly mentioned 'brave' browser
✅ Launching Brave Browser...
```

That's it! Enjoy your LLM-powered desktop agent! 🎉
