import ast
import os
import sys
from rich.console import Console
from rich.table import Table

console = Console()

class GreenCodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.reports = []
        self.imported_modules = set()
        self.used_modules = set()

    def visit_Import(self, node):
        for alias in node.names:
            self.imported_modules.add(alias.name)
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        self.imported_modules.add(node.module)
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Load):
            self.used_modules.add(node.id)
        self.generic_visit(node)

    def visit_For(self, node):
        # Rule: Detect Nested Loops (High Energy Consumption)
        for child in ast.walk(node):
            if isinstance(child, ast.For) and child is not node:
                self.reports.append({
                    "line": node.lineno,
                    "issue": "Nested Loop Detected",
                    "impact": "High CPU usage / Energy Intensive",
                    "fix": "Try to flatten the loop or use vectorization (NumPy)."
                })
        self.generic_visit(node)

def analyze_file(filepath):
    with open(filepath, "r") as f:
        tree = ast.parse(f.read())
    
    analyzer = GreenCodeAnalyzer()
    analyzer.visit(tree)
    
    # Check for unused imports (Energy waste at startup)
    unused = analyzer.imported_modules - analyzer.used_modules
    for mod in unused:
        analyzer.reports.append({
            "line": "N/A",
            "issue": f"Unused Import: {mod}",
            "impact": "Unnecessary Memory & Startup Energy",
            "fix": f"Remove 'import {mod}'"
        })
    
    return analyzer.reports

def display_report(reports, filename):
    table = Table(title=f"Green Audit Report: {filename}")
    table.add_column("Line", style="cyan")
    table.add_column("Issue", style="red")
    table.add_column("Sustainability Impact", style="yellow")
    table.add_column("Green Fix", style="green")

    for r in reports:
        table.add_row(str(r['line']), r['issue'], r['impact'], r['fix'])

    console.print(table)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 green_analyzer.py <file_to_scan.py>")
    else:
        file_to_scan = sys.argv[1]
        results = analyze_file(file_to_scan)
        display_report(results, file_to_scan)