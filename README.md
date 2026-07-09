# 🛠️ Technical Debt Hotspot Analyzer

![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.9+-blue?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

## What is this tool?
Everyone talks about **Technical Debt**, but very few know how to *quantify* it in practice. This autonomous Python script solves exactly that problem. 

It is a Static Analysis CLI tool that runs against any Git Repository and mathematically calculates the "Hotspots"—the files and dependencies that cost your engineering team the most time and money.

## Core Features & The Mathematics of Debt

The tool evaluates your codebase based on three primary pillars of Technical Debt:

### 1. 🧠 Code Complexity vs. Git Churn (The Hotspot Score)
The tool calculates a mathematical **Debt Score** for every Python file by combining:
* **Cyclomatic Complexity (via `radon`):** How convoluted and difficult to read the code is (if/else branching, loops, nested logic).
* **Git Churn (via `git log`):** How frequently the file is modified by developers.

> **💡 The Hotspot Rule:** A highly complex file that hasn't been touched in 3 years is *NOT* a severe problem (it's legacy, but stable). However, a highly complex file that changes *every week* is a ticking time bomb.

**The Formula:** `Debt Score = Complexity * (log(Churn) + 1)`

### 2. 📝 TODO / FIXME Tracker (Human Debt)
Developers often leave comments like `# TODO`, `# FIXME`, or `# HACK`. The analyzer scans the entire codebase to sum up the unresolved human debt left behind.

### 3. 🛡️ Dependency Decay Monitor (Security Debt)
Old libraries introduce security vulnerabilities and maintenance headaches. The analyzer parses your `requirements.txt`, connects to the **PyPI API**, checks the latest available versions of your packages, and flags dependencies that are outdated.

## 🚀 Quick Start

1. Install the requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the analyzer inside any Git Repository:
   ```bash
   python analyzer.py /path/to/your/repo
   ```
   *(If you omit the path, it will analyze the current directory).*

### Output
The tool prints a stunning color-coded report to your Terminal (powered by `rich`) and exports a permanent **`debt_report.md`** file detailing your Top 10 Hotspots and your Outdated Dependencies.

---
*Built for true software engineering observability by DARKAIS.*
