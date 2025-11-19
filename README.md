# AI Academy Agentic System

A Python 3.12-based autonomous agent system built on top of Retrieval-Augmented Generation (RAG). The system features a modular architecture with support for contextual data pipelines, reasoning loops with self-reflection, tool-calling capabilities, and evaluation frameworks.

## Features

- **Document Processing**: Load and process PDF documents and MP4 video transcripts
- **Vector Embeddings**: Generate and store embeddings using OpenAI for efficient retrieval
- **ChromaDB Integration**: Persistent vector database for semantic search
- **RAG Pipeline**: Retrieve relevant context and generate responses using OpenAI GPT
- **Audio Transcription**: OpenAI Whisper API integration for MP4 audio transcription
- **Smart Caching**: Transcript caching with modification tracking and partial transcript resume capability
- **Query Logging**: Automatic logging of all queries and responses to `queries.log` with timestamps
- **CLI Interface**: Rich terminal interface with progress bars and formatted output using typer and rich

## Quick Start

```bash
# 1. Setup environment
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY

# 2. Activate virtual environment
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# 3. Add your documents to data/hw4_docs/ directory
# (PDFs and MP4 files)

# 4. Build the search index
python -m scripts.build_index build

# 5. Verify index was created
python -m scripts.build_index stats
```

📘 **For complete command reference, see [COMMANDS.md](COMMANDS.md)**

## Project Structure

```
ai-academy-agent-capstone-project/
├── agent/                  # Core agent logic
│   ├── orchestrator.py    # Main agent coordinator
│   ├── reasoning.py       # Planning and decomposition
│   ├── reflection.py      # Self-critique
│   └── memory.py          # State tracking
├── tools/                  # Tool-calling system
│   ├── registry.py        # Tool registration
│   ├── rag_tools.py       # Vector search tools
│   └── utility_tools.py   # Calculator, date, etc.
├── rag/                    # RAG modules
│   ├── config.py          # Configuration management
│   ├── loaders.py         # Document loading
│   ├── embeddings.py      # Vector embeddings
│   ├── retriever.py       # Document retrieval
│   └── prompts.py         # Prompt templates
├── evaluation/            # Metrics and testing
│   ├── metrics.py         # Scoring functions
│   └── evaluator.py       # Evaluation runner
├── scripts/               # CLI tools
│   ├── build_index.py     # Index building
│   ├── demo.py            # Agent demo
│   └── legacy_chatbot.py  # RAG chatbot
├── data/                  # Training data
│   ├── hw4_docs/          # Document storage
│   ├── ai_academy/        # Additional materials
│   └── transcripts/       # Cached MP4 transcripts
├── docs/                  # Architecture documentation
├── logs/                  # Agent execution logs
├── embeddings/            # ChromaDB storage
├── .env.example           # Environment template
├── COMMANDS.md            # Command reference
├── requirements.txt       # Dependencies
└── README.md              # This file
```

## Prerequisites

- Python 3.12 or higher
- OpenAI API key (get one from [OpenAI Platform](https://platform.openai.com/))
- ffmpeg (for MP4 audio extraction)
  - macOS: `brew install ffmpeg`
  - Linux: `apt-get install ffmpeg` or `yum install ffmpeg`
  - Windows: Download from [ffmpeg.org](https://ffmpeg.org/)

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/Votok/ai-academy-rag-chatbot.git
cd ai-academy-rag-chatbot
```

### 2. Create a Virtual Environment

Create and activate a virtual environment to isolate project dependencies:

**On Linux/MacOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**On Windows:**

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Install Dependencies

Install all required packages from requirements.txt:

```bash
pip install -r requirements.txt
```

This will install:

- `langchain` - Framework for building LLM applications
- `openai` - OpenAI API client (includes Whisper API access)
- `chromadb` - Vector database for embeddings
- `pypdf` - PDF document processing
- `tiktoken` - Token counting for OpenAI models
- `python-dotenv` - Environment variable management
- `typer` - CLI framework for command-line interface
- `rich` - Rich terminal formatting and progress bars
- `tqdm` - Progress bars for data processing
- `ffmpeg-python` - Audio extraction from MP4 files

### 4. Configure Environment Variables

Create a `.env` file from the template:

```bash
cp .env.example .env
```

Edit the `.env` file and add your OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-api-key-here
```

⚠️ **Important**: Never commit your `.env` file to version control. It's already listed in `.gitignore`.

#### Configuration Options

The application supports the following configuration parameters (all optional except `OPENAI_API_KEY`):

**OpenAI API Settings:**
- `OPENAI_API_KEY` (required): Your OpenAI API key from https://platform.openai.com/api-keys
- `GPT_MODEL` (default: `gpt-4`): Model for answer generation. Options: `gpt-4`, `gpt-4-turbo`, `gpt-3.5-turbo`
- `EMBEDDING_MODEL` (default: `text-embedding-3-small`): Model for embeddings. Options: `text-embedding-3-small`, `text-embedding-3-large`, `text-embedding-ada-002`
- `WHISPER_MODEL` (default: `whisper-1`): Model for audio transcription

**Directory Paths:**
- `DATA_DIR` (default: `./data`): Location of source documents (PDFs and MP4 files)
- `CHROMA_DB_DIR` (default: `./embeddings`): Vector database storage location

**Text Processing:**
- `CHUNK_SIZE` (default: `1000`): Maximum size of text chunks in characters. Larger chunks provide more context but may reduce retrieval precision.
- `CHUNK_OVERLAP` (default: `200`): Character overlap between chunks to maintain context continuity

**Retrieval:**
- `TOP_K` (default: `5`): Number of most relevant chunks to retrieve per query. Higher values provide more context but increase token usage and cost.

See `.env.example` for a complete configuration template with detailed comments.

## Usage

### Building the Index

After adding your PDF and MP4 files to the `data/hw4_docs/` directory:

```bash
# Build or update the index (incremental)
python -m scripts.build_index build

# Rebuild from scratch (if you changed chunking parameters)
python -m scripts.build_index build --rebuild

# Check index statistics
python -m scripts.build_index stats
```

**Output example:**
```
Found 1 PDF(s) and 1 MP4(s)
Loading 1 PDF file(s)...
✓ Databases for GenAI.pdf: 20 pages
Processing 1 MP4 file(s)...
✓ Using cached transcript for video.mp4
✓ Created 51 chunks from 21 documents
✓ Successfully indexed 51/51 new documents
```

### Querying the Chatbot

After building the index, you can query the chatbot:

```bash
# Ask a question (default command)
python -m scripts.legacy_chatbot "What is a vector database?"

# Or use explicit query command
python -m scripts.legacy_chatbot query "What is RAG?"

# Retrieve more context chunks
python -m scripts.legacy_chatbot query "How does retrieval work?" --top-k 10

# Use custom log file
python -m scripts.legacy_chatbot query "Explain embeddings" --log-file my_queries.log
```

The chatbot will:
1. Retrieve the most relevant document chunks
2. Generate an answer using GPT with context
3. Display the answer with source citations
4. Show relevance scores for retrieved chunks
5. Log the full query and response to `queries.log`

### Testing Individual Components

```bash
# Test embeddings generation
python -m rag.embeddings

# Test document loading and chunking
python -m rag.loaders

# Test retrieval from index
python -m rag.retriever
```

### Advanced Usage

```bash
# Use custom parameters (requires rebuild)
CHUNK_SIZE=1500 CHUNK_OVERLAP=300 python -m scripts.build_index build --rebuild

# Use different embedding model
EMBEDDING_MODEL=text-embedding-3-large python -m scripts.build_index build --rebuild

# Get more retrieval results
TOP_K=10 python -c "from rag.retriever import retrieve_relevant_chunks; ..."
```

### Query Logging

All chatbot queries are automatically logged to `queries.log` in the project root directory. Each log entry includes:

- **Timestamp**: When the query was made
- **Question**: The user's original question
- **Answer**: The generated response
- **Sources**: List of source files used (PDFs and MP4s)
- **Retrieved Chunks**: Details of each chunk including relevance scores
- **Metadata**: Model used and time elapsed

**Example log entry format:**
```
================================================================================
TIMESTAMP: 2025-11-18 14:30:22
================================================================================
QUESTION: What is RAG?
...
ANSWER:
Retrieval-Augmented Generation (RAG) is...
...
SOURCES (2 file(s)):
  - lecture_notes.pdf
  - course_video.mp4
...
```

**Custom log file:**
```bash
python -m scripts.legacy_chatbot query "question" --log-file custom_queries.log
```

📘 **For the complete command reference with troubleshooting guides, see [COMMANDS.md](COMMANDS.md)**

## Common Commands

### Index Management

| Command | Purpose |
|---------|---------|
| `python -m scripts.build_index build` | Build or update the search index |
| `python -m scripts.build_index stats` | Show index statistics |
| `python -m scripts.build_index build --rebuild` | Rebuild index from scratch |
| `python -m scripts.build_index clear` | Delete all indexed documents |

### Chatbot Queries

| Command | Purpose |
|---------|---------|
| `python -m scripts.legacy_chatbot "question"` | Ask a question (default command) |
| `python -m scripts.legacy_chatbot query "question"` | Ask a question (explicit) |
| `python -m scripts.legacy_chatbot query "question" --top-k 10` | Retrieve more context chunks |
| `python -m scripts.legacy_chatbot query "question" --log-file path` | Use custom log file |
| `python -m scripts.legacy_chatbot build-index` | Build index via chatbot CLI |

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.
