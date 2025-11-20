# Agent Demo Guide

A comprehensive guide to using the AI Academy Agent demo CLI to showcase the agent's capabilities.

## Quick Start

### Prerequisites

1. Ensure your environment is set up:
```bash
source .venv/bin/activate
```

2. Build the search index (if not already done):
```bash
python -m scripts.build_index build
```

3. Verify your `.env` file has `OPENAI_API_KEY` configured

## Available Commands

### 1. Ask a Question

Ask the agent a single question and get an answer:

```bash
python -m scripts.demo ask "What is RAG?"
```

**With verbose mode** (shows reasoning steps):
```bash
python -m scripts.demo ask "What is RAG?" --verbose
```

**With trace saving** (saves execution trace to logs/):
```bash
python -m scripts.demo ask "What is RAG?" --save-trace
```

### 2. Interactive Mode

Start an interactive REPL session:

```bash
python -m scripts.demo interactive
```

In interactive mode:
- Type your questions and press Enter
- Type `quit`, `exit`, or `q` to exit
- Answers are displayed with confidence scores

### 3. Run Example Queries

Run pre-configured example queries that demonstrate different capabilities:

```bash
python -m scripts.demo examples
```

This presents a menu with options:
1. **Simple Factual Query** - Basic RAG question
2. **Contextual Course Query** - Searches specific course materials
3. **Multi-Step Reasoning** - Requires analysis and comparison
4. **Tool Calling Example** - Demonstrates calculator tool usage
5. **All** - Run all examples sequentially

### 4. Workflow Visualization

Show detailed step-by-step workflow for a query:

```bash
python -m scripts.demo workflow "How does RAG work?"
```

This command:
- Shows all reasoning steps
- Displays workflow summary table
- Presents final answer with metadata

### 5. View Statistics

Display agent and knowledge base statistics:

```bash
python -m scripts.demo stats
```

Shows:
- Knowledge base collections and document counts
- Available tools and their categories

---

## Example Usage Scenarios

### Simple Factual Query

```bash
python -m scripts.demo ask "What is retrieval-augmented generation?"
```

**Expected behavior:**
- Agent searches vector database for relevant context
- Generates concise answer explaining RAG
- Displays confidence score and metadata

### Course-Specific Question

```bash
python -m scripts.demo ask "What did I learn about embeddings in Week 2?"
```

**Expected behavior:**
- Agent identifies relevant course collection
- Retrieves Week 2 materials
- Summarizes embedding concepts from that lesson

### Tool Usage Example

```bash
python -m scripts.demo ask "Calculate 15% of 250" --verbose
```

**Expected behavior:**
- Agent identifies calculator tool is needed
- Calls CalculatorTool with expression "250 * 0.15"
- Returns result: 37.5
- Verbose mode shows tool calling process

### Multi-Step Reasoning

```bash
python -m scripts.demo ask "Compare RAG and standard prompting. List 3 differences." --verbose
```

**Expected behavior:**
- Agent plans comparison task
- Retrieves context about both approaches
- Generates structured comparison with 3 key differences
- Shows reasoning steps in verbose mode

---

## Command Options

### Global Options

All commands support standard CLI features:
- `--help` - Show command help
- Auto-completion (if configured)

### Ask Command Options

```bash
python -m scripts.demo ask [QUERY] [OPTIONS]
```

**Options:**
- `-v, --verbose` - Show detailed reasoning steps
- `-s, --save-trace` - Save execution trace to file

**Examples:**
```bash
# Basic query
python -m scripts.demo ask "What is RAG?"

# With verbose output
python -m scripts.demo ask "What is RAG?" -v

# Save trace
python -m scripts.demo ask "What is RAG?" -s

# Both verbose and save trace
python -m scripts.demo ask "What is RAG?" -v -s
```

---

## Understanding the Output

### Standard Output Format

```
🤖 AI Academy Agent
Ask me anything about the AI Academy course materials!

Your question: What is RAG?

[Thinking... spinner animation]

============================================================
🎯 Answer:
============================================================

[Markdown-formatted answer]

------------------------------------------------------------
Confidence: 0.85 | Iterations: 1 | Steps: 5
```

### Verbose Output

When using `--verbose`, you'll see:
- **Phase 1: Planning** - Query decomposition
- **Phase 2: Retrieval** - Document search results
- **Phase 3: Tool Calling** - Tool selection and execution (if needed)
- **Phase 4: Generation** - Answer generation
- **Phase 5: Reflection** - Self-critique
- **Phase 6: Revision** - Revision decision (if needed)

### Workflow Summary Table

The `workflow` command displays a table:

```
┌───┬──────────┬─────────────────────────────────────┐
│ # │ Type     │ Summary                              │
├───┼──────────┼─────────────────────────────────────┤
│ 1 │ plan     │ Main goal: Explain RAG concept...    │
│ 2 │ retrieve │ Retrieved 5 documents...             │
│ 3 │ generate │ Generated 450 characters...          │
│ 4 │ reflect  │ Confidence: 0.85...                  │
└───┴──────────┴─────────────────────────────────────┘
```

---

## Tips and Best Practices

### 1. Use Verbose Mode for Debugging

When testing or debugging, always use `--verbose`:
```bash
python -m scripts.demo ask "your query" --verbose
```

This helps you understand:
- What collections are being searched
- Whether tools are being called
- How the agent is reasoning
- Why it's making revisions

### 2. Interactive Mode for Exploration

Use interactive mode for exploratory conversations:
```bash
python -m scripts.demo interactive
```

This is ideal for:
- Testing multiple related queries
- Iterative refinement of questions
- Quick experimentation

### 3. Save Traces for Analysis

For important queries, save traces:
```bash
python -m scripts.demo ask "complex query" --save-trace
```

Traces are saved to `logs/trace_TIMESTAMP.json` and include:
- Full reasoning steps
- Tool calls and results
- Reflection feedback
- Final confidence score

### 4. Use Examples for Demos

When demonstrating to others:
```bash
python -m scripts.demo examples
```

Select option 5 to run all examples and show:
- RAG capabilities
- Tool usage
- Multi-step reasoning
- Reflection and revision

---

## Troubleshooting

### Issue: "No collections found"

**Solution:** Build the search index first:
```bash
python -m scripts.build_index build
```

### Issue: OpenAI API errors

**Solution:** Check your `.env` file:
```bash
# Verify OPENAI_API_KEY is set
cat .env | grep OPENAI_API_KEY
```

### Issue: Module import errors

**Solution:** Ensure virtual environment is activated:
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### Issue: Verbose mode shows empty collections

**Solution:** Verify data directory has documents:
```bash
ls data/*.pdf data/*.mp4
```

Then rebuild index:
```bash
python -m scripts.build_index build --rebuild
```

---

## Advanced Usage

### Custom Query Patterns

**Ask for explanations:**
```bash
python -m scripts.demo ask "Explain how vector embeddings work"
```

**Request comparisons:**
```bash
python -m scripts.demo ask "Compare semantic search vs keyword search"
```

**Ask for summaries:**
```bash
python -m scripts.demo ask "Summarize the key concepts from Week 3"
```

**Request calculations:**
```bash
python -m scripts.demo ask "What is 23% of 456?"
```

**Ask for current information:**
```bash
python -m scripts.demo ask "What is today's date?"
```

### Combining Features

```bash
# Verbose + Save trace for complete analysis
python -m scripts.demo ask "Complex query requiring multiple tools" -v -s

# Workflow visualization with verbose output
python -m scripts.demo workflow "Multi-step reasoning query"
```

---

## What Each Command Demonstrates

### `ask` - Basic Agent Capabilities
- Query understanding
- Context retrieval
- Answer generation
- Confidence scoring

### `interactive` - Conversational Mode
- REPL interface
- Stateless interactions (each query is independent)
- Quick experimentation

### `examples` - Showcase Features
- Pre-configured queries demonstrating all capabilities
- Great for demos and presentations
- Shows tool usage, reasoning, and reflection

### `workflow` - Detailed Visualization
- Step-by-step execution trace
- Reasoning step breakdown
- Complete workflow transparency

### `stats` - System Information
- Knowledge base status
- Available tools
- Collection statistics

---

## Next Steps

After familiarizing yourself with the demo CLI:

1. **Explore your data**: Use `ask` to query your specific course materials
2. **Test tool usage**: Try calculation and formatting queries
3. **Analyze reasoning**: Use `workflow` to understand agent decisions
4. **Save important traces**: Use `--save-trace` for complex queries
5. **Present to others**: Use `examples` for demonstrations

For more information, see:
- `README.md` - Project overview
- `COMMANDS.md` - Complete command reference
- `MASTER_PLAN.md` - Implementation roadmap
- `CLAUDE.md` - Development guidelines

---

**Demo Guide Version**: 1.0
**Last Updated**: 2025-11-20
**Phase**: 8 - Interactive Demo CLI
