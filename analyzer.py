import os
import sys
import subprocess
import math
import requests
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

def check_dependencies_decay(repo_path):
    """
    Checks requirements.txt against PyPI to find outdated packages and calculates a decay score.
    """
    req_file = repo_path / 'requirements.txt'
    if not req_file.exists():
        return []
        
    decay_results = []
    
    with open(req_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    console.print("[cyan]Checking dependencies for decay...[/cyan]")
    
    for line in track(lines, description="Querying PyPI..."):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        # Parse requirement (e.g. requests==2.28.0, radon>=5.1.0)
        import re
        match = re.split(r'==|>=|<=|>|<|~=', line)
        pkg_name = match[0].strip()
        current_version = match[1].strip() if len(match) > 1 else "Unknown"
        
        if current_version == "Unknown":
            continue
            
        try:
            # Query PyPI
            response = requests.get(f"https://pypi.org/pypi/{pkg_name}/json", timeout=5)
            if response.status_code == 200:
                data = response.json()
                latest_version = data['info']['version']
                
                # Simple decay metric: Are they exactly the same string?
                # (A real implementation would parse SemVer and weight major/minor diffs)
                if current_version != latest_version and not current_version.startswith(latest_version):
                    decay_results.append({
                        'package': pkg_name,
                        'current': current_version,
                        'latest': latest_version,
                        'status': 'Outdated'
                    })
        except Exception:
            pass
            
    return decay_results


def analyze_repo(repo_path):
    repo_path = Path(repo_path).resolve()
    
    if not (repo_path / '.git').exists():
        console.print(f"[red]Error: {repo_path} is not a valid Git repository![/red]")
        sys.exit(1)
        
    console.print(Panel.fit(f"Analyzing Technical Debt in: [bold cyan]{repo_path}[/bold cyan]"))
    
    py_files = list(repo_path.rglob('*.py'))
    py_files = [f for f in py_files if not any(part.startswith('.') or part in ('venv', 'env', '__pycache__') for part in f.relative_to(repo_path).parts)]
    
    if not py_files:
        console.print("[yellow]No python files found to analyze.[/yellow]")
        return [], 0, check_dependencies_decay(repo_path)
        
    results = []
    total_todos = 0
    
    for file_path in track(py_files, description="Scanning files..."):
        rel_path = file_path.relative_to(repo_path)
        
        complexity = get_cyclomatic_complexity(file_path)
        churn = get_git_churn(file_path, repo_path)
        todos = scan_for_todos(file_path)
        total_todos += todos
        
        if complexity == 0:
            continue
            
        debt_score = complexity * (math.log1p(churn) + 1)
        
        results.append({
            'file': str(rel_path),
            'complexity': complexity,
            'churn': churn,
            'todos': todos,
            'score': round(debt_score, 2)
        })
        
    results.sort(key=lambda x: x['score'], reverse=True)
    decay_results = check_dependencies_decay(repo_path)
    
    return results, total_todos, decay_results

def print_report(results, total_todos, decay_results, repo_path):
    report_content = f"# 🛠️ Technical Debt Report\\n\\n"
    report_content += f"**Repository Analyzed:** `{repo_path}`\\n"
    report_content += f"**Total Unresolved TODOs/FIXMEs:** {total_todos}\\n\\n"
    
    # 1. Hotspots Table
    if results:
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
                str(i), res['file'], str(res['complexity']), str(res['churn']), str(res['todos']), str(res['score'])
            )
            
        console.print(table)
        
        report_content += "## 🔥 Top Hotspots\\n"
        report_content += "These files have the highest combination of Code Complexity and Git Commit Churn.\\n\\n"
        report_content += "| Rank | File Path | Complexity | Git Churn | TODOs | Debt Score |\\n"
        report_content += "|---|---|---|---|---|---|\\n"
        for i, res in enumerate(top_hotspots, 1):
            report_content += f"| {i} | `{res['file']}` | {res['complexity']} | {res['churn']} | {res['todos']} | **{res['score']}** |\\n"
    else:
        console.print("[green]No significant code hotspots found![/green]")
        report_content += "## 🔥 Top Hotspots\\n*No significant hotspots found.*\\n"
        
    console.print(f"\\n[bold]Total unresolved TODOs/FIXMEs found:[/bold] [yellow]{total_todos}[/yellow]\\n")
    
    # 2. Dependency Decay Table
    if decay_results:
        decay_table = Table(title="Dependency Decay (Security & Maintenance Debt)", show_header=True, header_style="bold yellow")
        decay_table.add_column("Package", style="cyan")
        decay_table.add_column("Current Version", justify="center", style="red")
        decay_table.add_column("Latest on PyPI", justify="center", style="green")
        decay_table.add_column("Status", style="bold red")
        
        for dep in decay_results:
            decay_table.add_row(dep['package'], dep['current'], dep['latest'], dep['status'])
            
        console.print(decay_table)
        
        report_content += "\\n## 🛡️ Dependency Decay Monitor\\n"
        report_content += "Outdated packages representing Security & Maintenance Debt.\\n\\n"
        report_content += "| Package | Current Version | Latest Version | Status |\\n"
        report_content += "|---|---|---|---|\\n"
        for dep in decay_results:
            report_content += f"| `{dep['package']}` | {dep['current']} | {dep['latest']} | ⚠️ {dep['status']} |\\n"
    else:
        report_content += "\\n## 🛡️ Dependency Decay Monitor\\n*No outdated dependencies found.*\\n"
        
    # Write to File
    with open(repo_path / 'debt_report.md', 'w', encoding='utf-8') as f:
        f.write(report_content)
        
    console.print("\\n[green]Report generated successfully at `debt_report.md`![/green]")

if __name__ == "__main__":
    target_repo = sys.argv[1] if len(sys.argv) > 1 else "."
    results, todos, decay_results = analyze_repo(target_repo)
    print_report(results, todos, decay_results, Path(target_repo).resolve())
