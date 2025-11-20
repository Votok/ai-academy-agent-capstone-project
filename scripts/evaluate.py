"""Evaluation runner script.

This module runs agent evaluation on test datasets:
- Load test queries from evaluation/test_queries.json
- Execute agent on each query
- Compute performance metrics (answer quality, reasoning, tools)
- Generate evaluation reports with summary statistics
- Save results to evaluation/reports/

Usage:
    python -m scripts.evaluate
    python -m scripts.evaluate --verbose
    python -m scripts.evaluate --output evaluation/reports/custom.json
"""

import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from pathlib import Path

from evaluation.evaluator import EvaluationRunner

app = typer.Typer(help="Agent Evaluation Runner")
console = Console()


@app.command()
def run(
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output during evaluation"),
    save: bool = typer.Option(True, "--save/--no-save", help="Save results to file"),
    output: str = typer.Option(None, "--output", "-o", help="Custom output file path"),
    dataset: str = typer.Option(None, "--dataset", "-d", help="Custom test queries JSON file")
):
    """Run agent evaluation on test queries"""

    console.print(Panel.fit(
        "[bold blue]🧪 Agent Evaluation System[/bold blue]\n"
        "Evaluating agent performance on test query dataset",
        border_style="blue"
    ))

    # Initialize runner
    runner = EvaluationRunner(test_queries_path=dataset)

    # Run evaluation
    console.print("\n[yellow]Running evaluation...[/yellow]")
    results = runner.run_evaluation(verbose=verbose)

    # Display summary
    summary = results["summary"]

    console.print("\n" + "=" * 60)
    console.print("[bold green]📊 EVALUATION SUMMARY[/bold green]")
    console.print("=" * 60)

    console.print(f"\n[bold]Total Queries:[/bold] {summary['total_queries']}")

    # Answer Quality Table
    console.print("\n[bold cyan]📝 Answer Quality Scores[/bold cyan]")
    quality_table = Table(show_header=True, header_style="bold magenta")
    quality_table.add_column("Metric", style="cyan", width=15)
    quality_table.add_column("Score", style="green", justify="right", width=10)

    for metric, score in summary["answer_quality"].items():
        # Color code based on score
        if score >= 0.8:
            score_str = f"[green]{score:.3f}[/green]"
        elif score >= 0.6:
            score_str = f"[yellow]{score:.3f}[/yellow]"
        else:
            score_str = f"[red]{score:.3f}[/red]"

        quality_table.add_row(metric.capitalize(), score_str)

    console.print(quality_table)

    # Reasoning Stats
    console.print("\n[bold cyan]🧠 Reasoning Performance[/bold cyan]")
    reasoning_table = Table(show_header=True, header_style="bold magenta")
    reasoning_table.add_column("Metric", style="cyan", width=15)
    reasoning_table.add_column("Value", style="green", justify="right", width=10)

    reasoning_table.add_row("Avg Iterations", f"{summary['reasoning']['avg_iterations']:.2f}")
    reasoning_table.add_row("Avg Confidence", f"{summary['reasoning']['avg_confidence']:.3f}")
    reasoning_table.add_row("Avg Efficiency", f"{summary['reasoning']['avg_efficiency']:.3f}")

    console.print(reasoning_table)

    # Tool Usage Stats
    console.print("\n[bold cyan]🔧 Tool Usage[/bold cyan]")
    tool_table = Table(show_header=True, header_style="bold magenta")
    tool_table.add_column("Metric", style="cyan", width=20)
    tool_table.add_column("Value", style="green", justify="right", width=10)

    tool_table.add_row("Queries using tools", str(summary['tools']['queries_using_tools']))
    tool_table.add_row("Tool usage rate", f"{summary['tools']['tool_usage_rate']:.3f}")
    tool_table.add_row("Avg success rate", f"{summary['tools']['avg_success_rate']:.3f}")

    console.print(tool_table)

    # Topic Coverage
    console.print("\n[bold cyan]📚 Topic Coverage[/bold cyan]")
    console.print(f"  Average: [green]{summary['topic_coverage']['average']:.3f}[/green]")

    # Save results
    if save:
        output_path = runner.save_results(results, output_path=output)
        console.print(f"\n[green]✓ Results saved to:[/green] {output_path}")

    console.print("\n[bold green]✅ Evaluation complete![/bold green]")


@app.command()
def show(
    report: str = typer.Argument(..., help="Path to evaluation report JSON file")
):
    """Display a saved evaluation report"""

    if not Path(report).exists():
        console.print(f"[red]Error: Report file not found: {report}[/red]")
        raise typer.Exit(code=1)

    import json
    with open(report, 'r') as f:
        results = json.load(f)

    summary = results.get("summary", {})
    timestamp = results.get("timestamp", "Unknown")

    console.print(Panel.fit(
        f"[bold blue]📊 Evaluation Report[/bold blue]\n"
        f"Timestamp: {timestamp}\n"
        f"Total Queries: {summary.get('total_queries', 0)}",
        border_style="blue"
    ))

    # Display summary (similar to run command)
    console.print("\n[bold cyan]📝 Answer Quality Scores[/bold cyan]")
    for metric, score in summary.get("answer_quality", {}).items():
        console.print(f"  {metric.capitalize()}: {score:.3f}")

    console.print("\n[bold cyan]🧠 Reasoning Performance[/bold cyan]")
    for metric, value in summary.get("reasoning", {}).items():
        console.print(f"  {metric}: {value}")

    console.print("\n[bold cyan]🔧 Tool Usage[/bold cyan]")
    for metric, value in summary.get("tools", {}).items():
        console.print(f"  {metric}: {value}")


if __name__ == "__main__":
    app()
