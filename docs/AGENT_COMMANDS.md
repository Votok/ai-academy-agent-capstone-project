# AI Agent Commands - Quick Reference

A concise cheat sheet for working with the AI Academy Agent system.

---

## 🚀 Quick Start

```bash
# 1. Setup (one-time)
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 2. Activate environment
source .venv/bin/activate

# 3. Build search index
python -m scripts.build_index build

# 4. Try the agent
python -m scripts.demo ask "What is RAG?"
```

---

## 🤖 Agent Demo CLI

### Ask a Question
```bash
# Basic query
python -m scripts.demo ask "What is RAG?"

# With verbose mode (shows reasoning steps)
python -m scripts.demo ask "Calculate 15% of 250" --verbose

# Save execution trace
python -m scripts.demo ask "Your question" --save-trace
```

### Interactive Mode
```bash
# Start REPL for multiple queries
python -m scripts.demo interactive

# Type 'quit' or 'q' to exit
```

### Run Examples
```bash
# Menu of pre-configured demos
python -m scripts.demo examples

# Showcases: RAG queries, tool usage, reasoning
```

### Workflow Visualization
```bash
# Show detailed step-by-step execution
python -m scripts.demo workflow "How does RAG work?"

# Displays: planning, retrieval, tools, generation, reflection
```

### System Statistics
```bash
# View collections and tools
python -m scripts.demo stats
```

**What each command does:**
- `ask` → Single question with optional verbose/trace
- `interactive` → Continuous conversation mode
- `examples` → Pre-configured demo scenarios
- `workflow` → Detailed execution visualization
- `stats` → System status (collections, tools)

---

## 📊 Index Management

### Build or Update Index
```bash
# Incremental build (fast - skips existing)
python -m scripts.build_index build

# Build specific collection
python -m scripts.build_index build --collection transcripts

# Force rebuild from scratch
python -m scripts.build_index build --rebuild
```

**When to use:**
- `build` → After adding new documents to data/
- `build --rebuild` → After changing CHUNK_SIZE or CHUNK_OVERLAP
- `build --collection NAME` → Update specific collection

### Check Index Status
```bash
# Show all collections
python -m scripts.build_index stats

# Show specific collection
python -m scripts.build_index stats --collection ai_academy_course
```

### Clear Collection
```bash
# Delete all documents from a collection
python -m scripts.build_index clear --collection old_data --yes
```

---

## 📈 Evaluation

### Run Agent Evaluation
```bash
# Evaluate on test queries
python -m scripts.evaluate run

# With verbose output
python -m scripts.evaluate run --verbose

# Save to custom location
python -m scripts.evaluate run --output evaluation/reports/my_eval.json
```

### View Saved Report
```bash
# Display evaluation results
python -m scripts.evaluate show evaluation/reports/eval_20251120_164530.json
```

**What it tests:**
- Answer quality (LLM-as-judge)
- Tool usage effectiveness
- Reasoning efficiency
- Topic coverage

---

## ⚙️ Configuration

### Verify Setup
```bash
# Check configuration is loaded
python -c "from rag.config import print_config; print_config()"

# Test API key works
python -c "from rag.embeddings import embed_query; print('✓ API valid')"
```

### View Data Directory
```bash
# List source files
ls -lah data/

# Check collections exist
ls -la embeddings/
```

---

## 🧪 Testing Components

### Test Agent System
```bash
# Test orchestrator
python -m agent.orchestrator

# Test reasoning loop
python -m agent.reasoning_loop

# Test tool registry
python tests/test_tools.py
```

### Test RAG System
```bash
# Test document loading
python -m rag.loaders

# Test retrieval
python -m rag.retriever

# Test collections
python -m rag.collections
```

---

## 🔧 Troubleshooting

### Problem: No collections found
```bash
# Solution: Build index first
python -m scripts.build_index build
python -m scripts.demo stats  # Verify
```

### Problem: API key error
```bash
# Solution: Check .env file
cat .env | grep OPENAI_API_KEY

# Verify it's set
python -c "from rag.config import OPENAI_API_KEY; print(OPENAI_API_KEY[:10])"
```

### Problem: Import errors
```bash
# Solution: Activate virtual environment
source .venv/bin/activate
pip install -r requirements.txt
```

### Problem: Poor answer quality
```bash
# Solution 1: Check retrieval results
python -m scripts.demo ask "Your query" --verbose

# Solution 2: Rebuild with different chunk size
# Edit .env: CHUNK_SIZE=1500
python -m scripts.build_index build --rebuild

# Solution 3: Check collection stats
python -m scripts.demo stats
```

### Problem: MP4 transcription fails
```bash
# Check ffmpeg installed
ffmpeg -version

# Clear transcript cache and retry
rm -rf data/transcripts/
python -m scripts.build_index build --rebuild
```

---

## 📖 Common Workflows

### First Time Setup
```bash
cp .env.example .env              # 1. Create config
# Edit .env with OPENAI_API_KEY   # 2. Add API key
source .venv/bin/activate         # 3. Activate env
python -m scripts.build_index build  # 4. Build index
python -m scripts.demo stats      # 5. Verify
python -m scripts.demo ask "Test" # 6. Try it
```

### Adding New Documents
```bash
cp ~/Downloads/*.pdf data/        # 1. Add files
python -m scripts.build_index build  # 2. Update index
python -m scripts.demo stats      # 3. Verify
```

### Demo for Presentation
```bash
# Option 1: Run all examples
python -m scripts.demo examples
# Select option 5 (All)

# Option 2: Show specific workflow
python -m scripts.demo workflow "What is retrieval-augmented generation?"
```

### Debugging Agent Behavior
```bash
# Step 1: Run with verbose
python -m scripts.demo ask "Your query" --verbose

# Step 2: Save trace for analysis
python -m scripts.demo ask "Your query" --save-trace
# Check logs/trace_TIMESTAMP.json

# Step 3: Check what was retrieved
python -m scripts.demo workflow "Your query"
```

---

## 📝 Quick Reference Card

```
╔═══════════════════════════════════════════════════════════╗
║  ESSENTIAL AGENT COMMANDS                                 ║
╠═══════════════════════════════════════════════════════════╣
║  Agent CLI:                                               ║
║    Ask question:        python -m scripts.demo ask "..."  ║
║    Interactive mode:    python -m scripts.demo interactive║
║    Show examples:       python -m scripts.demo examples   ║
║    Visualize workflow:  python -m scripts.demo workflow   ║
║    System stats:        python -m scripts.demo stats      ║
║                                                            ║
║  Index Management:                                        ║
║    Build index:         python -m scripts.build_index build║
║    Show stats:          python -m scripts.build_index stats║
║    Rebuild scratch:     python -m scripts.build_index build --rebuild║
║                                                            ║
║  Evaluation:                                              ║
║    Run eval:            python -m scripts.evaluate run    ║
║    Show report:         python -m scripts.evaluate show FILE║
╚═══════════════════════════════════════════════════════════╝
```

---

## 🎯 Command Categories

| Category | Key Commands | Use When |
|----------|-------------|----------|
| **Agent** | `demo ask`, `demo interactive` | Querying the agent |
| **Demo** | `demo examples`, `demo workflow` | Presentations, debugging |
| **Index** | `build_index build`, `build_index stats` | Managing data |
| **Eval** | `evaluate run`, `evaluate show` | Testing performance |
| **Config** | `print_config()` | Verifying setup |

---

## 🔑 Key Features by Command

### `demo ask`
- Single-shot questions
- Optional verbose mode shows all reasoning steps
- Save traces for debugging
- Returns: answer + confidence + metadata

### `demo interactive`
- REPL for multiple questions
- Stateless (each query independent)
- Quick exploration
- Type 'quit' to exit

### `demo examples`
- 4 pre-configured demos
- Showcases: RAG, tools, reasoning, reflection
- Run individually or all at once
- Great for presentations

### `demo workflow`
- Shows complete 7-phase pipeline
- Table of reasoning steps
- Useful for understanding agent decisions
- Always runs in verbose mode

### `demo stats`
- Lists all collections + document counts
- Shows 6 registered tools with categories
- Quick health check
- No API calls needed

---

## 📚 Additional Resources

- **Complete Guide**: [docs/DEMO_GUIDE.md](DEMO_GUIDE.md)
- **Project Overview**: [README.md](../README.md)
- **Development Guide**: [CLAUDE.md](../CLAUDE.md)
- **Implementation Plan**: [MASTER_PLAN.md](../MASTER_PLAN.md)

---

## 💡 Pro Tips

1. **Use verbose mode** when debugging: `--verbose` shows all reasoning steps
2. **Save traces** for complex queries: `--save-trace` creates JSON logs
3. **Check stats first**: Run `demo stats` to verify collections exist
4. **Rebuild sparingly**: Only use `--rebuild` after config changes
5. **Interactive for exploration**: Use `demo interactive` for related queries

---

**Version**: 1.0
**Last Updated**: 2025-11-20
