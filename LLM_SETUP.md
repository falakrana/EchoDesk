# LLM Integration Setup Guide (Groq)

## Overview
The AI Desktop Agent supports **Groq LLMs** via LangChain for intelligent natural language understanding. This allows the agent to understand commands like "I want to use brave" and correctly identify which application to launch.

## Features
- **Intelligent Intent Recognition**: Uses Groq-hosted models to understand natural language
- **Automatic Fallback**: Falls back to rule-based extraction if LLM fails
- **Structured Output**: Returns goal, confidence score, and reasoning
- **Secure**: LLM never sees file paths or system commands

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

This will install:
- `langchain` - LLM orchestration framework
- `langchain-groq` - Groq integration
- `python-dotenv` - Environment variable management

### 2. Get Groq API Key
1. Visit the Groq Console: https://console.groq.com/keys
2. Sign in and create an API key
3. Copy your API key

### 3. Configure Environment Variables
Create a `.env` file in the project root (repository folder, e.g. `echo-desk`, next to `main.py`):

```bash
# Copy the example file
copy .env.example .env
```

Edit `.env` and add your API key:
```
GROQ_API_KEY=your_actual_api_key_here
```

### 4. Run the Agent
```bash
python main.py
```

Primary entry point is `main.py`. For conversational mode with `ConversationalAgent`, use `python main_chat.py` (see [QUICKSTART.md](QUICKSTART.md#entry-points)).

## How It Works

### Architecture
```
User Input → LLM Interpreter → Policy Decision → Registry Validator → Safe Executor
```

### LLM Interpreter Flow
1. **User Input**: "I want to use brave"
2. **LLM Processing**: Groq model analyzes the input
3. **Structured Output**:
   ```json
   {
     "goal": "launch_brave",
     "app_name": "brave",
     "confidence": 0.95,
     "reasoning": "User explicitly mentioned 'brave' browser"
   }
   ```
4. **Policy Decision**: Maps "launch_brave" to application name
5. **Registry Validation**: Checks if "brave" exists in registry
6. **Execution**: Launches the validated application

## Configuration Options

### Enable/Disable LLM
By default, LLM is enabled. To disable it:

```python
interpreter = NaturalLanguageInterpreter(use_llm=False)
```

### Change Model
To use a different Groq model:

```python
interpreter = NaturalLanguageInterpreter(llm_model="llama-3.1-8b-instant")
```

Available model examples:
- `llama-3.1-8b-instant` - Fast and efficient
- `llama-3.3-70b-versatile` - More capable

## Fallback Behavior

The system has multiple fallback layers:

1. **LLM Available**: Uses Groq for interpretation
2. **LLM Fails**: Falls back to rule-based pattern matching
3. **No API Key**: Automatically uses rule-based extraction
4. **Dependencies Missing**: Uses rule-based extraction

## Security Model

The LLM integration maintains strict security:

- ✅ **LLM sees**: Only user's natural language input
- ❌ **LLM never sees**: File paths, executables, system commands
- ✅ **LLM outputs**: Only goal and confidence (structured JSON)
- ❌ **LLM never outputs**: Commands or paths to execute

The LLM's **only job** is to understand user intent. All execution decisions are made by the Policy Engine and validated against the registry.

## Testing

Run the test script to verify LLM integration:

```bash
python llm/test_llm_interpreter.py
```

This will test various inputs and show:
- Goal extraction
- Confidence scores
- LLM reasoning
- Comparison with rule-based approach

## Troubleshooting

### "GROQ_API_KEY not set"
- Make sure you created a `.env` file
- Verify the API key is correct
- Check the file is in the project root (same directory as `main.py`)

### "LangChain not available"
- Run `pip install -r requirements.txt`
- Verify installation: `pip list | grep langchain-groq`

### LLM extraction fails
- Check your internet connection
- Verify API key is valid
- The system will automatically fall back to rule-based extraction

## Next Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Get API key**: Visit Groq Console
3. **Create `.env` file**: Add your Groq API key
4. **Test it**: Run `python main.py` and try "I want to use brave"

Enjoy your LLM-powered desktop agent! 🚀
