"""Demo CLI for the agent system.

This module provides an interactive command-line interface to demonstrate
the agent's capabilities:
- Interactive query processing
- Step-by-step workflow visualization
- Verbose debugging mode
- Rich terminal output

Usage:
    python -m scripts.demo ask "Your question here"
    python -m scripts.demo ask "Calculate 15% of 250" --verbose
    python -m scripts.demo workflow "What did I learn in Week 3?"
    python -m scripts.demo interactive
    python -m scripts.demo examples
    python -m scripts.demo stats
"""

import typer
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.markdown import Markdown
from typing import Optional
import time

from agent.orchestrator import AgentOrchestrator

app = typer.Typer(help="🤖 AI Academy Agent Demo")
console = Console()


@app.command()
def ask(
    query: str = typer.Argument(..., help="Your question"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show reasoning steps"),
    save_trace: bool = typer.Option(False, "--save-trace", "-s", help="Save execution trace"),
):
    """
    Ask the agent a question

    Example:
        python -m scripts.demo ask "What is RAG?"
    """
    console.print(Panel.fit(
        f"[bold cyan]🤖 AI Academy Agent[/bold cyan]\n"
        f"[dim]Ask me anything about the AI Academy course materials![/dim]",
        border_style="cyan"
    ))

    console.print(f"\n[bold]Your question:[/bold] {query}\n")

    # Initialize agent
    orchestrator = AgentOrchestrator()

    # Run agent with progress indicator
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        task = progress.add_task("[cyan]Thinking...", total=None)

        state = orchestrator.run(query, verbose=verbose)

        progress.update(task, completed=True)

    # Display answer
    console.print("\n" + "="*60)
    console.print("[bold green]🎯 Answer:[/bold green]")
    console.print("="*60 + "\n")

    # Render as markdown
    md = Markdown(state.current_answer)
    console.print(md)

    # Display metadata
    console.print("\n" + "-"*60)
    console.print(f"[dim]Confidence: {state.confidence_score:.2f} | "
                  f"Iterations: {state.iteration} | "
                  f"Steps: {len(state.reasoning_steps)}[/dim]")

    # Save trace if requested
    if save_trace:
        trace_path = orchestrator.save_trace(state)
        console.print(f"[dim]Trace saved: {trace_path}[/dim]")


@app.command()
def interactive():
    """
    Start interactive mode (REPL)

    Example:
        python -m scripts.demo interactive
    """
    console.print(Panel.fit(
        f"[bold cyan]🤖 AI Academy Agent - Interactive Mode[/bold cyan]\n"
        f"[dim]Type your questions or 'quit' to exit[/dim]",
        border_style="cyan"
    ))

    orchestrator = AgentOrchestrator()

    while True:
        console.print()
        query = typer.prompt("You", default="").strip()

        if query.lower() in ["quit", "exit", "q"]:
            console.print("[yellow]Goodbye! 👋[/yellow]")
            break

        if not query:
            continue

        # Run agent
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Thinking...", total=None)
            state = orchestrator.run(query, verbose=False)
            progress.update(task, completed=True)

        # Display answer
        console.print(f"\n[bold green]Agent:[/bold green]")
        md = Markdown(state.current_answer)
        console.print(md)
        console.print(f"\n[dim]Confidence: {state.confidence_score:.2f}[/dim]")


@app.command()
def examples():
    """
    Run example queries demonstrating agent capabilities
    """
    console.print(Panel.fit(
        f"[bold cyan]🤖 Agent Demo - Example Queries[/bold cyan]",
        border_style="cyan"
    ))

    examples_list = [
        {
            "name": "Simple Factual Query",
            "query": "What is retrieval-augmented generation?",
            "description": "Basic RAG question"
        },
        {
            "name": "Contextual Course Query",
            "query": "What did I learn about embeddings in Week 2 of the AI Academy course?",
            "description": "Requires searching specific course materials"
        },
        {
            "name": "Multi-Step Reasoning",
            "query": "How does RAG differ from standard prompting? List 3 key differences.",
            "description": "Requires analysis and comparison"
        },
        {
            "name": "Tool Calling Example",
            "query": "Calculate 15% of 250",
            "description": "Demonstrates calculator tool usage"
        }
    ]

    # Display menu
    table = Table(title="Available Examples")
    table.add_column("#", style="cyan", width=4)
    table.add_column("Name", style="green")
    table.add_column("Description", style="dim")

    for i, ex in enumerate(examples_list, 1):
        table.add_row(str(i), ex["name"], ex["description"])

    table.add_row("5", "All", "Run all examples")

    console.print(table)

    # Get selection
    choice = typer.prompt("\nSelect example", type=int, default=1)

    if choice == 5:
        # Run all
        orchestrator = AgentOrchestrator()
        for i, ex in enumerate(examples_list, 1):
            console.print(f"\n{'='*60}")
            console.print(f"[bold]Example {i}: {ex['name']}[/bold]")
            console.print(f"[dim]{ex['description']}[/dim]")
            console.print(f"{'='*60}\n")
            console.print(f"[bold cyan]Query:[/bold cyan] {ex['query']}\n")

            state = orchestrator.run(ex["query"], verbose=True)

            console.print("\n[bold green]Answer:[/bold green]")
            md = Markdown(state.current_answer)
            console.print(md)
            console.print(f"\n[dim]Confidence: {state.confidence_score:.2f} | Iterations: {state.iteration}[/dim]")

            if i < len(examples_list):
                if not typer.confirm("\nContinue to next example?", default=True):
                    break

    elif 1 <= choice <= len(examples_list):
        # Run selected example
        ex = examples_list[choice - 1]
        console.print(f"\n[bold]{ex['name']}[/bold]")
        console.print(f"[dim]{ex['description']}[/dim]\n")
        console.print(f"[bold cyan]Query:[/bold cyan] {ex['query']}\n")

        orchestrator = AgentOrchestrator()
        state = orchestrator.run(ex["query"], verbose=True)

        console.print("\n[bold green]Answer:[/bold green]")
        md = Markdown(state.current_answer)
        console.print(md)


@app.command()
def workflow(
    query: str = typer.Argument(..., help="Your question"),
):
    """
    Show detailed workflow visualization for a query

    Example:
        python -m scripts.demo workflow "What is RAG?"
    """
    console.print(Panel.fit(
        f"[bold cyan]🤖 Agent Workflow Visualization[/bold cyan]",
        border_style="cyan"
    ))

    console.print(f"\n[bold]Query:[/bold] {query}\n")

    orchestrator = AgentOrchestrator()

    # Run with verbose
    console.print("[bold blue]Starting workflow...[/bold blue]\n")
    state = orchestrator.run(query, verbose=True)

    # Visualize steps
    console.print("\n" + "="*60)
    console.print("[bold green]📊 Workflow Summary[/bold green]")
    console.print("="*60 + "\n")

    steps_table = Table(title="Reasoning Steps")
    steps_table.add_column("#", style="cyan", width=4)
    steps_table.add_column("Type", style="green")
    steps_table.add_column("Summary", style="white")

    for step in state.reasoning_steps:
        summary = step.content[:60] + "..." if len(step.content) > 60 else step.content
        steps_table.add_row(
            str(step.step_number),
            step.step_type,
            summary
        )

    console.print(steps_table)

    # Final answer
    console.print("\n[bold green]🎯 Final Answer:[/bold green]")
    md = Markdown(state.current_answer)
    console.print(md)

    console.print(f"\n[dim]Total Steps: {len(state.reasoning_steps)} | "
                  f"Iterations: {state.iteration} | "
                  f"Confidence: {state.confidence_score:.2f}[/dim]")


@app.command()
def stats():
    """
    Show agent and knowledge base statistics
    """
    console.print(Panel.fit(
        f"[bold cyan]📊 Agent Statistics[/bold cyan]",
        border_style="cyan"
    ))

    # Collection stats
    from rag import collections

    console.print("\n[bold]Knowledge Base Collections:[/bold]\n")

    try:
        collection_names = collections.list_collections()

        if collection_names:
            table = Table()
            table.add_column("Collection", style="cyan")
            table.add_column("Documents", style="green")

            for collection_name in collection_names:
                stats = collections.get_collection_stats(collection_name)
                doc_count = stats.get("count", 0)
                table.add_row(collection_name, str(doc_count))

            console.print(table)
        else:
            console.print("[dim]No collections found. Run 'python -m scripts.build_index build' first.[/dim]")
    except Exception as e:
        console.print(f"[dim red]Error accessing collections: {e}[/dim red]")

    # Tool stats
    from tools import get_global_registry
    registry = get_global_registry()

    console.print("\n[bold]Available Tools:[/bold]\n")

    tools_table = Table()
    tools_table.add_column("Tool Name", style="cyan")
    tools_table.add_column("Category", style="green")

    for tool_name in registry.list_tools():
        tool = registry.get_tool(tool_name)
        tools_table.add_row(tool_name, tool.category.value if hasattr(tool, 'category') else "N/A")

    console.print(tools_table)


if __name__ == "__main__":
    app()
