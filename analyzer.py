import os
import sys
import subprocess
import math
from pathlib import Path
from radon.complexity import cc_visit
from radon.visitors import Function, Class
from rich.console import Console
from rich.table import Table
from rich.progress import track
from rich.panel import Panel

console = Console()

def get_git_churn(file_path, repo_path):
    """
    Returns the number of commits that have touched the given file.
    If the file is not tracked or has no commits, returns 0.
    """
    try:
        # Run git log --oneline -- <file> | wc -l
        result = subprocess.run(
            ['git', 'log', '--oneline', '--', str(file_path)],
            cwd=repo_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        if result.returncode != 0:
            return 0
        lines = [line for line in result.stdout.split('\\n') if line.strip()]
        return len(lines)
    except Exception:
        return 0

def get_cyclomatic_complexity(file_path):
    """
    Calculates the total cyclomatic complexity of a Python file using Radon.
    Returns the sum of complexity of all functions/classes.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        blocks = cc_visit(code)
        
        total_complexity = 0
        for block in blocks:
            if isinstance(block, (Function, Class)):
                total_complexity += block.complexity
                
        return total_complexity
    except Exception:
        # If there's a syntax error or unable to read, return 0
        return 0

def scan_for_todos(file_path):
    """
    Scans a file line by line and counts TODO, FIXME, and HACK keywords.
    """
    todos = 0
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                upper_line = line.upper()
                if 'TODO' in upper_line or 'FIXME' in upper_line or 'HACK' in upper_line:
                    todos += 1
        return todos
    except Exception:
        return 0

def analyze_repo(repo_path):
    repo_path = Path(repo_path).resolve()
    
    # Check if it's a git repo
    if not (repo_path / '.git').exists():
        console.print(f"[red]Error: {repo_path} is not a valid Git repository![/red]")
        sys.exit(1)
        
    console.print(Panel.fit(f"Analyzing Technical Debt in: [bold cyan]{repo_path}[/bold cyan]"))
    
    # Find all Python files
    py_files = list(repo_path.rglob('*.py'))
    
    # Filter out virtual environments and hidden dirs (only looking at relative path)
    py_files = [f for f in py_files if not any(part.startswith('.') or part in ('venv', 'env', '__pycache__') for part in f.relative_to(repo_path).parts)]
    
    if not py_files:
        console.print("[yellow]No python files found to analyze.[/yellow]")
        sys.exit(0)
        
    results = []
    total_todos = 0
    
    for file_path in track(py_files, description="Scanning files..."):
        rel_path = file_path.relative_to(repo_path)
        
        complexity = get_cyclomatic_complexity(file_path)
        churn = get_git_churn(file_path, repo_path)
        todos = scan_for_todos(file_path)
        total_todos += todos
        
        # Avoid penalizing files with no complexity
        if complexity == 0:
            continue
            
        # The Mathematical Formula for Technical Debt Score
        # High complexity * frequent changes = High Debt Score
        debt_score = complexity * (math.log1p(churn) + 1)
        
        results.append({
            'file': str(rel_path),
            'complexity': complexity,
            'churn': churn,
            'todos': todos,
            'score': round(debt_score, 2)
        })
        
    # Sort by debt score descending
    results.sort(key=lambda x: x['score'], reverse=True)
    
    return results, total_todos

def print_report(results, total_todos, repo_path):
    if not results:
        console.print("[green]Your codebase looks incredibly clean. No significant debt hotspots found![/green]")
        return
        
    top_hotspots = results[:10]
    
    table = Table(title="Top Technical Debt Hotspots", show_header=True, header_style="bold magenta")
    table.add_column("Rank", justify="center")
    table.add_column("File Path", style="cyan")
    table.add_column("Complexity", justify="right", style="red")
    table.add_column("Git Churn", justify="right", style="yellow")
    table.add_column("TODOs", justify="right")
    table.add_column("Debt Score", justify="right", style="bold red")
    
    for i, res in enumerate(top_hotspots, 1):
        table.add_row(
            str(i),
            res['file'],
            str(res['complexity']),
            str(res['churn']),
            str(res['todos']),
            str(res['score'])
        )
        
    console.print(table)
    console.print(f"\\n[bold]Total unresolved TODOs/FIXMEs found:[/bold] [yellow]{total_todos}[/yellow]")
    
    # Generate Markdown Report
    report_content = f"# 🛠️ Technical Debt Report\\n\\n"
    report_content += f"**Repository Analyzed:** `{repo_path}`\\n"
    report_content += f"**Total Unresolved TODOs:** {total_todos}\\n\\n"
    report_content += "## 🔥 Top Hotspots\\n"
    report_content += "These files have the highest combination of Code Complexity and Git Commit Churn.\\n\\n"
    report_content += "| Rank | File Path | Complexity | Git Churn | TODOs | Debt Score |\\n"
    report_content += "|---|---|---|---|---|---|\\n"
    
    for i, res in enumerate(top_hotspots, 1):
        report_content += f"| {i} | `{res['file']}` | {res['complexity']} | {res['churn']} | {res['todos']} | **{res['score']}** |\\n"
        
    with open(repo_path / 'debt_report.md', 'w', encoding='utf-8') as f:
        f.write(report_content)
        
    console.print("\\n[green]Report generated successfully at `debt_report.md`![/green]")

if __name__ == "__main__":
    target_repo = sys.argv[1] if len(sys.argv) > 1 else "."
    results, todos = analyze_repo(target_repo)
    print_report(results, todos, Path(target_repo).resolve())
