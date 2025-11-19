"""Dependency validation script for AI Academy Agentic System.

This script checks that all required packages are installed and importable,
and that all custom modules can be loaded successfully.

Usage:
    python scripts/check_dependencies.py
"""

import sys


def check_dependencies() -> bool:
    """Check all dependencies import successfully.

    Returns:
        True if all checks passed, False otherwise
    """
    results = []

    # Core dependencies (same as HW4 baseline!)
    packages = [
        ("langchain", "LangChain core"),
        ("langchain_community", "LangChain community"),
        ("langchain_openai", "LangChain OpenAI"),
        ("openai", "OpenAI API"),
        ("chromadb", "ChromaDB"),
        ("pypdf", "PyPDF"),
        ("tiktoken", "Tiktoken"),
        ("dotenv", "Python-dotenv"),
        ("typer", "Typer CLI"),
        ("rich", "Rich terminal"),
        ("tqdm", "TQDM progress"),
        ("ffmpeg", "FFmpeg Python"),
    ]

    print("=== Checking External Dependencies ===")
    for package, name in packages:
        try:
            __import__(package)
            results.append((name, True, None))
            print(f"✓ {name}")
        except ImportError as e:
            results.append((name, False, str(e)))
            print(f"✗ {name}: {e}")

    # Custom modules
    custom_modules = [
        ("rag.config", "RAG Config"),
        ("rag.embeddings", "RAG Embeddings"),
        ("rag.retriever", "RAG Retriever"),
        ("rag.loaders", "RAG Loaders"),
        ("rag.prompts", "RAG Prompts"),
    ]

    print("\n=== Checking Custom Modules ===")
    for module, name in custom_modules:
        try:
            __import__(module)
            results.append((name, True, None))
            print(f"✓ {name}")
        except ImportError as e:
            results.append((name, False, str(e)))
            print(f"✗ {name}: {e}")

    # Check for failures
    failures = [(name, err) for name, success, err in results if not success]

    print(f"\n{'=' * 50}")
    if failures:
        print(f"❌ {len(failures)} dependency check(s) failed:")
        for name, err in failures:
            print(f"   - {name}: {err}")
        print(f"{'=' * 50}")
        return False
    else:
        print(f"✅ All {len(results)} dependency checks passed")
        print(f"{'=' * 50}")
        return True


if __name__ == "__main__":
    success = check_dependencies()
    sys.exit(0 if success else 1)
