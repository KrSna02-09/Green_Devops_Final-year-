import time
import psutil
import os
import ast
from database_manager import init_db, log_metric
import subprocess
from rich.console import Console
from rich.table import Table

console = Console()

# Constants for Calculation (Standard estimates for a laptop/server)
# Avg CPU Power (Watts) for a standard laptop is ~20W-40W
AVG_CPU_POWER_W = 30.0 
# India's Carbon Intensity (approx 700g CO2 per kWh)
CARBON_INTENSITY_G_KWH = 708 

def measure_carbon_impact(func, *args):
    """Measures the estimated carbon footprint of a function execution."""
    start_time = time.perf_counter()
    start_cpu = psutil.cpu_percent(interval=None)
    
    # Execute the code
    result = func(*args)
    
    end_time = time.perf_counter()
    duration_sec = end_time - start_time
    
    # 1. Convert seconds to hours
    duration_hours = duration_sec / 3600
    
    # 2. Energy (kWh) = (Power in Watts / 1000) * Time in Hours
    energy_kwh = (AVG_CPU_POWER_W / 1000) * duration_hours
    
    # 3. Carbon Footprint (grams of CO2) = Energy * Carbon Intensity
    carbon_emitted_mg = (energy_kwh * CARBON_INTENSITY_G_KWH) * 1000 # converting to mg for visibility
    
    return {
        "duration": round(duration_sec, 4),
        "energy_kwh": energy_kwh,
        "co2_mg": round(carbon_emitted_mg, 4)
    }

# --- This is just a sample 'Bad' function to test our analyzer ---
def inefficient_task():
    total = 0
    for i in range(10**6): # Simulating a heavy task
        total += i
    return total

if __name__ == "__main__":
    # 1. Initialize the Database
    init_db()
    
    # 2. Identify the current version (Git Commit)
    try:
        commit_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode('ascii').strip()
    except Exception:
        commit_hash = "local-dev"

    console.print(f"\n[bold green]Starting Green Audit for Commit: {commit_hash[:7]}[/bold green]")
    
    # 3. Run Measurement (Only once!)
    metrics = measure_carbon_impact(inefficient_task)
    
    # 4. Save the results to SQLite
    # We'll pass '2' as a placeholder for code smells found by the AST
    log_metric(commit_hash, metrics['duration'], metrics['energy_kwh'], metrics['co2_mg'], 2)
    
    # 5. Display the Pretty Table
    table = Table(title="Execution Sustainability Metrics")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="yellow")
    
    table.add_row("Execution Time", f"{metrics['duration']} seconds")
    table.add_row("Estimated Energy", f"{metrics['energy_kwh']:.8f} kWh")
    table.add_row("Carbon Footprint", f"{metrics['co2_mg']} mg of CO2")
    
    console.print(table)