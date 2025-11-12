# 🧠 SPIRAL Autonomous Intelligence Guide

## Overview
SPIRAL now has **autonomous intelligence** similar to GitHub Copilot CLI. It understands context, searches your filesystem, and reasons about what you need.

## Three-Layer Intelligence System

### Layer 1: Context Understanding
SPIRAL analyzes your conversation history to understand what you're referring to:

```
You: "I created a template called my_cert"
You: "Now populate it"         ← SPIRAL knows you mean my_cert
```

**What it tracks:**
- Recently mentioned files
- Current task (create/read/modify/analyze/find)
- Conversation topics
- Working directory context

### Layer 2: Filesystem Search
If context isn't enough, SPIRAL autonomously searches your PC:

```
You: "find my EICR files"
SPIRAL: 🔍 Searching filesystem...
        ✅ Found 10 EICR files in Downloads/
```

**Smart search features:**
- Searches multiple relevant locations
- Filters by file type and keywords
- Ranks by confidence/relevance
- Shows top matches with summaries

### Layer 3: AI Generation
Only if context and filesystem don't have the answer, SPIRAL uses AI:

```
You: "explain BS7671 regulation 411.4.5"
SPIRAL: 🤖 Using AI reasoning...
        [Generates expert explanation]
```

## Natural Language Examples

### File Discovery
```
You: "find my EICR files"
You: "show me certificate PDFs in Downloads"
You: "what templates do I have?"
You: "locate configuration files"
```

SPIRAL will:
1. Understand what you're looking for
2. Search appropriate directories
3. Show ranked results with confidence scores

### Contextual References
```
You: "/template-new id=my_cert title='EICR'"
You: "now show me that file"              ← Knows which file
You: "populate it with data from Downloads"  ← Auto-finds source
```

### Task Execution
```
You: "I want to populate the EICR template"
```

SPIRAL will:
1. ✅ Analyze task: populate_template (85% confidence)
2. 🔍 Find template files automatically
3. 🔍 Find source data (PDFs/Excel)
4. 💡 Suggest next steps:
   - Extract data from source
   - Map fields to template
   - Validate and generate output

## How It Works

### Autonomous Discovery
```
You: "populate the template"
```

**SPIRAL's thought process:**
1. 🧠 Check conversation: was a template mentioned recently?
2. 🔍 Search filesystem: find .template.json files
3. 🔍 Search for data: find EICR PDFs/Excel files
4. ✅ Present options: "Found template X and data Y, proceed?"

### Multi-Domain Search
SPIRAL knows where to look for different things:

| What you need | Where SPIRAL searches |
|--------------|----------------------|
| EICR files | ~/Downloads, ~/Documents |
| Templates | ./templates, ~/Documents/spiral_codex_unified/templates |
| Code files | Current directory, ~/Documents |
| Configs | ./config, ~/.config, ~/Documents/config |

### Confidence Scoring
Every discovery has a confidence score:

- **90-100%**: Exact match (e.g., recently mentioned file)
- **70-89%**: High confidence (filename + extension match)
- **50-69%**: Medium (keyword match)
- **30-49%**: Low (partial match)

SPIRAL only auto-executes on 75%+ confidence.

## Comparison to GitHub Copilot CLI

| Feature | GitHub Copilot CLI | SPIRAL |
|---------|-------------------|--------|
| Natural language | ✅ | ✅ |
| Context awareness | ✅ | ✅ |
| File discovery | ✅ | ✅ |
| Task understanding | ✅ | ✅ |
| Domain-specific (BS7671) | ❌ | ✅ |
| Filesystem reasoning | Limited | ✅ Full search |
| Confidence scoring | Hidden | ✅ Visible |
| Multi-layer fallback | AI-only | Context → Files → AI |

## Advanced Features

### 1. Contextual File References
```
You: "scan ~/Downloads/cert.pdf"
You: "what's in that file?"        ← Remembers cert.pdf
You: "extract the circuit data"    ← Still referring to cert.pdf
```

### 2. Task Continuity
```
You: "create an EICR certificate"
SPIRAL: Started task: create_certificate
        Step 1: Load template... ✅
        
You: "use the TN-C-S supply"      ← SPIRAL knows we're still creating cert
```

### 3. Intelligent Suggestions
```
You: "I have a PDF of an EICR"
SPIRAL: 💡 I can:
        1. Scan it and extract circuit data
        2. Validate against BS7671 standards
        3. Create a template from it
        Which would you like?
```

### 4. Error Recovery
```
You: "populate the template"
SPIRAL: 🔍 Found multiple templates:
        1. my_cert.template.json
        2. test_drop.template.json
        Which one?
        
You: "the first one"               ← Contextual understanding
SPIRAL: ✅ Using my_cert.template.json
```

## Usage Tips

### Be Natural
❌ Don't: `/find --type eicr --path ~/Downloads --recursive`
✅ Do: "find my EICR files"

### Build Context
Start conversations with context:
```
You: "I'm working on an EICR for 123 Main Street"
You: "scan the PDF in Downloads"    ← SPIRAL knows it's an EICR PDF
```

### Trust the Intelligence
SPIRAL will tell you when it's:
- 🧠 Using context
- 🔍 Searching filesystem  
- 🤖 Using AI

You don't need to micromanage!

### Verify Confidence
If SPIRAL shows low confidence (<70%), provide more context:
```
SPIRAL: Found file (45% confidence)
You: "the one from yesterday in Downloads"   ← More specific
SPIRAL: ✅ Found cert_2025-11-11.pdf (95% confidence)
```

## Examples in Action

### Complete EICR Workflow
```
You: "I need to create an EICR certificate"

SPIRAL: 🧠 Task: create_certificate
        🔍 Searching for templates...
        ✅ Found my_cert.template.json
        🔍 Need source data. Do you have a PDF or Excel file?

You: "yes, in Downloads"

SPIRAL: 🔍 Searching ~/Downloads for EICR files...
        ✅ Found eicr_sample.pdf (87% confidence)
        
        Next steps:
        1. Scan the PDF
        2. Extract circuit data
        3. Populate template
        
        Ready to proceed?

You: "yes"

SPIRAL: ✅ Scanning eicr_sample.pdf...
        ✅ Extracted 12 circuits
        ✅ Validated against BS7671
        ✅ Populated my_cert template
        📄 Output: templates/my_cert_2025-11-12.md
```

### Quick File Search
```
You: "where are my templates?"

SPIRAL: 🔍 Searching filesystem...
        ✅ Found 2 templates:
        
        📄 my_cert.template.json
           Location: /home/user/Documents/spiral_codex_unified/templates
           Type: EICR certificate template
           
        📄 test_drop.template.json  
           Location: /home/user/Documents/spiral_codex_unified/templates
           Type: Test template
```

## Technical Details

### Context Window
- Tracks last 10 messages
- Remembers mentioned files indefinitely per session
- Tracks current task state

### Search Algorithm
1. Determine search type from query keywords
2. Select relevant search domains
3. Walk directories (max depth: 3)
4. Match by: extension → keywords → patterns
5. Score confidence and rank results

### Reasoning Pipeline
```
User Query
    ↓
Check Context (recent files, current task)
    ↓ (if confidence < 70%)
Search Filesystem (smart domain selection)
    ↓ (if confidence < 60%)
Use AI Reasoning (with context injection)
    ↓
Present Result (with confidence & source)
```

## Debugging

To see SPIRAL's reasoning:
```
You: "explain your reasoning"
SPIRAL: 🧠 Reasoning Process:
        Confidence: 85%
        Source: filesystem
        Filesystem searched: Yes
        Evidence: 3 item(s)
          • /path/to/file1
          • /path/to/file2
        Files consulted: 2
```

## Summary

SPIRAL now thinks like a human assistant:
1. **Remember** what we discussed (context)
2. **Search** for information if needed (filesystem)
3. **Generate** answers as last resort (AI)

Just talk naturally, and SPIRAL will figure out what you need! 🚀
