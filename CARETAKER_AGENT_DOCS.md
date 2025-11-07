# 🧠 CARETAKER AGENT - Documentation

## What It Does

The Caretaker Agent is an invisible intelligence layer that monitors your conversation and automatically:

### 1. **Context Detection** 🎯
Analyzes your messages to detect conversation type:
- 💬 **Casual** - General chat
- ⚙️ **Technical** - Technical discussions
- 🚀 **DevOps** - Infrastructure/deployment
- 💻 **Coding** - Software development
- 🔧 **Debugging** - Problem solving
- 🎨 **Creative** - Creative work
- 📊 **Analysis** - Data analysis

### 2. **Silent Model Rotation** 🔄
When a model fails or hits rate limits:
- Automatically switches to backup models
- No error messages shown to you
- Tracks which models work best
- Learns from performance patterns

### 3. **Adaptive System Prompts** 🎭
Changes the AI's behavior based on context:
- **Casual**: Friendly and conversational
- **Technical**: Precise and detailed
- **DevOps**: Best practices focused
- **Coding**: Clean code and documentation
- **Debugging**: Systematic problem solving

### 4. **Context Shift Detection** 📈
Notices when conversation changes:
```
You: "Hi, how are you?"          → Casual 💬
You: "Explain REST APIs"         → Technical ⚙️
You: "Deploy with Docker"        → DevOps 🚀
You: "Write a Python function"   → Coding 💻
```

## How To Use

### Basic Usage:
```bash
cd ~/Documents/spiral_codex_unified
python spiral_intelligent.py
```

### What You'll See:
```
You: Hi, I'm Declan
Spiral 💬: [Casual response]

You: Explain how APIs work
Spiral ⚙️: [Technical response]

You: Create a REST API
Spiral 💻: [Coding response]
```

**Notice the emoji changes!** That's the only visible sign the caretaker is working.

## Under The Hood

### Context Detection Keywords:

**Technical** ⚙️:
- Keywords: api, protocol, architecture, system, algorithm
- Triggers: "how does", "explain the", "what is"

**DevOps** 🚀:
- Keywords: deploy, docker, kubernetes, pipeline, ci/cd
- Triggers: "how to deploy", "setup", "configure"

**Coding** 💻:
- Keywords: function, class, code, script, program
- Triggers: "write a", "create a", "build a"

**Debugging** 🔧:
- Keywords: error, bug, issue, problem, fix
- Triggers: "why is", "what's wrong", "how to fix"

### Model Rotation Strategy:

1. Tracks success/fail rate for each model
2. On failure, picks model with best success rate
3. Rotates through 5 models automatically
4. No error messages to user

### Performance Tracking:

Caretaker keeps statistics on:
- Which models work best
- Context transition patterns
- Conversation flow history

## Benefits

✅ **Seamless Experience**: No technical errors visible  
✅ **Context Aware**: Adapts to your needs automatically  
✅ **Self-Healing**: Handles rate limits silently  
✅ **Learning**: Improves model selection over time  
✅ **Smart**: Different behavior for different tasks  

## Comparison

| Feature | Old Chat | With Caretaker |
|---------|----------|----------------|
| Model rotation | Manual/errors | Silent/automatic |
| Context awareness | None | Full detection |
| Error handling | Shows errors | Handles silently |
| Adaptability | Static | Dynamic prompts |
| Learning | None | Performance tracking |

## Example Conversation

```
You: Hey Spiral, what's up?
Spiral 💬: Hey Declan! Not much, just here to help. What can I do for you?

You: Actually, I need to understand how Docker containers work
Spiral ⚙️: [Switches to technical mode automatically]
Docker containers are lightweight, isolated environments...

You: Can you write a Dockerfile for me?
Spiral 💻: [Switches to coding mode automatically]
Certainly! Here's a production-ready Dockerfile...

You: I'm getting an error when building
Spiral 🔧: [Switches to debugging mode automatically]
Let's troubleshoot this systematically...
```

## Advanced Features

### Context History
Caretaker logs all context transitions:
```json
{
  "from": "casual",
  "to": "technical",
  "timestamp": "2025-11-07T16:49:00Z"
}
```

### Model Performance
Tracks which models excel at which tasks:
```
google/gemini: 85% success (technical)
mistral: 90% success (coding)
```

### Intelligent Selection
Chooses best model for current context automatically.

## Future Enhancements

Coming soon:
- 🎯 Task-specific model selection
- 📊 Conversation analytics
- 🔮 Predictive context switching
- 💾 Long-term learning persistence

---

**The Caretaker works silently, like a good assistant should.** 🧠
