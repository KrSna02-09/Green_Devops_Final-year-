import sys
import time
import psutil
import os
import ast
import subprocess
from rich.console import Console
from rich.table import Table
from prometheus_client import CollectorRegistry, Gauge, push_to_gateway

# Local database import for backup logging
try:
    from database_manager import init_db, log_metric
except ImportError:
    pass 

console = Console()

# Constants
AVG_CPU_POWER_W = 30.0 
CARBON_INTENSITY_G_KWH = 708 

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
        for child in ast.walk(node):
            if isinstance(child, ast.For) and child is not node:
                self.reports.append({
                    "line": node.lineno,
                    "issue": "Nested Loop Detected",
                    "impact": "High CPU usage",
                    "fix": "Try to flatten the loop."
                })
        self.generic_visit(node)

def analyze_file(filepath):
    with open(filepath, "r") as f:
        tree = ast.parse(f.read())
    analyzer = GreenCodeAnalyzer()
    analyzer.visit(tree)
    unused = analyzer.imported_modules - analyzer.used_modules
    for mod in unused:
        analyzer.reports.append({"line": "N/A", "issue": f"Unused Import: {mod}", "impact": "Unnecessary Memory", "fix": "Remove import"})
    return analyzer.reports

# --- NEW FEATURE: Universal Subprocess Execution ---
def measure_subprocess_impact(filepath):
    start_time = time.perf_counter()
    try:
        # Dynamically execute ANY script passed to the analyzer
        subprocess.run([sys.executable, filepath], check=True, capture_output=True)
    except subprocess.CalledProcessError:
        console.print(f"[bold yellow]⚠️ Target script had internal errors, but energy was still measured.[/bold yellow]")
    except Exception as e:
        console.print(f"[bold red]⚠️ Execution failed: {e}[/bold red]")
        
    end_time = time.perf_counter()
    duration_sec = end_time - start_time
    duration_hours = duration_sec / 3600
    energy_kwh = (AVG_CPU_POWER_W / 1000) * duration_hours
    carbon_emitted_mg = (energy_kwh * CARBON_INTENSITY_G_KWH) * 1000
    return {"duration": round(duration_sec, 4), "energy_kwh": energy_kwh, "co2_mg": round(carbon_emitted_mg, 4)}

if __name__ == "__main__":
    try: init_db() 
    except: pass
    
    try:
        commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
    except Exception:
        commit_hash = "local-dev"

    # --- NEW FEATURE: Read target file from command line ---
    target_file = sys.argv[1] if len(sys.argv) > 1 else "test_code.py"

    console.print(f"\n[bold green]Starting Enterprise Green Audit on: {target_file}[/bold green]")
    
    # 1. Static Analysis
    ast_issues = analyze_file(target_file) if os.path.exists(target_file) else []
    smell_count = len(ast_issues)

    # 2. Measurement (Now uses the Universal wrapper)
    metrics = measure_subprocess_impact(target_file)
      
    # 3. --- ENTERPRISE PUSH TO GRAFANA ---
    try:
        registry = CollectorRegistry()
        Gauge('green_devops_co2_mg', 'CO2 Footprint', registry=registry).set(metrics['co2_mg'])
        Gauge('green_devops_energy_kwh', 'Energy Use', registry=registry).set(metrics['energy_kwh'])
        Gauge('green_devops_smells', 'Code Smells', registry=registry).set(smell_count)
        
        # Read the IP from GitHub Secrets (or default to localhost if testing locally)
        aws_ip = os.getenv('AWS_IP', 'localhost')
        
        push_to_gateway(f'{aws_ip}:9091', job=f'commit_{commit_hash[:7]}', registry=registry)
        console.print("[bold cyan]🚀 Metrics successfully pushed to Grafana![/bold cyan]")
    except Exception as e:
        console.print(f"[bold red]⚠️ Grafana telemetry push failed: {e}[/bold red]")

    # Optional: Keep local logging
    try: log_metric(commit_hash, metrics['duration'], metrics['energy_kwh'], metrics['co2_mg'], smell_count)
    except: pass

    # 4. Display Table
    table = Table(title=f"Execution Sustainability Metrics: {target_file}")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="yellow")
    table.add_row("Code Smells Found", str(smell_count))
    table.add_row("Execution Time", f"{metrics['duration']} seconds")
    table.add_row("Estimated Energy", f"{metrics['energy_kwh']:.8f} kWh")
    table.add_row("Carbon Footprint", f"{metrics['co2_mg']} mg of CO2")
    console.print(table)

    # 5. Quality Gate Logic
    score = 100
    if metrics['energy_kwh'] > 0.000005: score -= 20
    elif metrics['energy_kwh'] > 0.000002: score -= 10
    score -= (smell_count * 15)

    console.print("\n[bold]---- CI/CD Quality Gate ----[/bold]")
    if score >= 50:
        console.print(f"[bold green]✅ PASSED! Sustainability Score: {score}/100[/bold green]")
        sys.exit(0)
    else:
        console.print(f"[bold red]❌ FAILED! Sustainability Score: {score}/100[/bold red]")
        sys.exit(1)