# AI Academy Agentic System

An autonomous AI agent built on Retrieval-Augmented Generation (RAG) with reasoning loops, self-reflection, and tool-calling capabilities.

## Features

- Multi-collection RAG with ChromaDB vector search
- Autonomous reasoning with planning and self-reflection
- Tool-calling system (calculator, date, search, formatting)
- PDF and MP4 transcript processing with smart caching
- Interactive demo CLI with workflow visualization
- Evaluation framework with LLM-as-judge metrics

## Quick Start

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 2. Activate virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Add documents to data/ directory
# Place PDF and MP4 files in data/

# 5. Build the search index
python -m scripts.build_index build

# 6. Verify index
python -m scripts.build_index stats
```

**Prerequisites**: Python 3.12+, OpenAI API key, ffmpeg (for MP4 transcription: `brew install ffmpeg`)

## Project Structure

```
ai-academy-agent-capstone-project/
├── agent/              # Agent logic (orchestrator, reasoning, reflection)
├── tools/              # Tool system (6 registered tools)
├── rag/                # RAG modules (loaders, retriever, embeddings)
├── evaluation/         # Metrics and evaluation framework
├── scripts/            # CLI tools (build_index, demo)
├── data/               # Source documents (PDFs, MP4s)
│   └── transcripts/    # Auto-generated MP4 transcripts
├── embeddings/         # ChromaDB storage (gitignored)
├── logs/               # Agent execution traces
└── .env                # Environment config (never commit)
```

## Basic Commands

### Index Management

```bash
# Build or update index
python -m scripts.build_index build

# Build specific collection
python -m scripts.build_index build --collection transcripts

# Rebuild from scratch (after config changes)
python -m scripts.build_index build --rebuild

# Check all collection statistics
python -m scripts.build_index stats

# Show detailed workflow visualization
python -m scripts.demo workflow "How does RAG work?"
```

### LinkedIn Post Generator

Generate a LinkedIn post about completing the Ciklum AI Academy program:

````bash
# Generate post (displays in terminal)
python -m scripts.demo social


## Demo Workflow

The agent uses a 7-phase pipeline for processing queries:

1. **Planning** - Decompose query and identify sub-tasks
2. **Tool Selection** - Determine which tools are needed
3. **Retrieval** - Search vector database for relevant context
4. **Tool Execution** - Execute selected tools (calculator, date, etc.)
5. **Generation** - Generate answer using retrieved context and tool results
6. **Reflection** - Self-critique with confidence scoring
7. **Revision** - Refine answer if confidence is low (iterative loop)

### Workflow Visualization Example

The `workflow` command shows the complete agent pipeline:

```bash
python -m scripts.demo workflow "Compare RAG vs standard prompting"
````

**Output includes:**

- Step-by-step reasoning breakdown
- Retrieved documents with relevance scores
- Tool calls and results (if any)
- Reflection feedback and confidence score
- Workflow summary table showing all phases
- Final answer with metadata

**Sample workflow table:**

```
┌───┬──────────┬─────────────────────────────────────────┐
│ # │ Type     │ Summary                                 │
├───┼──────────┼─────────────────────────────────────────┤
│ 1 │ plan     │ Decomposed query into comparison task   │
│ 2 │ retrieve │ Retrieved 5 docs from ai_academy_course │
│ 3 │ generate │ Generated 520 chars answer              │
│ 4 │ reflect  │ Confidence: 0.88 - Answer is complete   │
└───┴──────────┴─────────────────────────────────────────┘
```

## License

MIT License - Open source and available for modification.
