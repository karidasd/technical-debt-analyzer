![Technical Debt Banner](tech_debt_banner.png)

# 🛠️ Technical Debt Hotspot Analyzer

![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

## 📖 The Philosophy: What is Technical Debt?
In Software Engineering, **Technical Debt** is the implied cost of additional rework caused by choosing an easy (limited) solution now instead of using a better approach that would take longer. 

Everyone talks about it, but very few teams know how to **quantify** it. Managers often ask: *"Where exactly is our technical debt, and how much is it costing us?"*

This tool is designed to answer that question empirically. It acts as an autonomous Static Analysis CLI tool that runs against any Git Repository and mathematically calculates the **"Hotspots"**—the specific files and dependencies that are silently draining your engineering team's time and money.

---

## ⚙️ How it Works: The Three Pillars of Debt

The analyzer evaluates your codebase across three distinct dimensions of software decay:

### 1. 🧠 Code Complexity vs. Git Churn (The Hotspot Score)
Not all messy code is technical debt. If you wrote a horrible, complex script 5 years ago, but it works perfectly and no one ever needs to touch it, that is *Legacy Code*, not dangerous Technical Debt. It costs you nothing today.

However, if a highly complex file is being edited by developers every single week, it is a **Ticking Time Bomb**. It causes bugs, slows down feature delivery, and burns out developers.

The tool calculates a mathematical **Debt Score** for every Python file by combining:
* **Cyclomatic Complexity (via `radon`):** How convoluted and difficult to read the code is (if/else branching, loops, nested logic).
* **Git Churn (via `git log`):** How frequently the file is modified by developers.

**The Formula:** 
```math
Debt Score = Complexity \times (\log(Churn) + 1)
```
*(We use logarithmic churn because 100 commits vs 10 commits is a big deal, but 1000 commits vs 900 commits is just normal activity).*

### 2. 📝 Human Debt (TODO / FIXME Tracker)
Developers often leave "IOUs" in the codebase disguised as comments like `# TODO`, `# FIXME`, `# HACK`, or `# XXX`. Over time, these accumulate and are forgotten. The analyzer scans the entire codebase to sum up this unresolved human debt, giving you a stark reminder of corners that were cut.

### 3. 🛡️ Security & Maintenance Debt (Dependency Decay Monitor)
Software rots over time if not maintained. Old libraries introduce security vulnerabilities, missing features, and compatibility issues. 
The analyzer parses your `requirements.txt`, connects to the **PyPI API (Python Package Index)** in real-time, fetches the absolute latest available versions of your packages, and flags dependencies that are outdated.

---

## 🚀 Quick Start Guide

### Installation
Clone this repository (or copy the `analyzer.py` into your own project) and install the dependencies:

```bash
git clone https://github.com/karidasd/technical-debt-analyzer.git
cd technical-debt-analyzer
pip install -r requirements.txt
```

### Running the Analyzer
Run the tool against any Git Repository on your machine.
```bash
# Analyze the current directory
python analyzer.py .

# Analyze a specific project folder
python analyzer.py /path/to/my/awesome/project
```

### The Output
The tool will process your history and output two things:
1. **A Stunning Terminal UI:** Powered by `rich`, showing progress bars and color-coded tables of your top hotspots directly in your console.
2. **A Markdown Report (`debt_report.md`):** A persistent file saved to the target directory containing your Top 10 Hotspot tables and your Outdated Dependencies, perfect for attaching to Jira tickets or GitHub Issues.

---

## 🛠️ CI/CD Integration Idea
You can integrate this script into your CI/CD pipeline (e.g., GitHub Actions). 
Have the pipeline run `analyzer.py` on every Friday night, and if the **Debt Score** of any file exceeds a certain threshold (e.g., > 100), automatically create a GitHub Issue assigning the engineering team to refactor it!

---
*Built for true software engineering observability by DARKAIS.*
