import json
import os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text

def render_trace(filepath: str):
    console = Console()
    
    if not os.path.exists(filepath):
        console.print(f"[red]Error: File {filepath} not found.[/red]")
        return
        
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        console.print(f"[red]Error loading JSON: {e}[/red]")
        return
        
    # Render Session Summary
    console.print(f"\n[bold blue]🚀 Lognote Flight Record[/bold blue]")
    console.print(f"Session Start: {data.get('session_start', 'Unknown')}")
    console.print(f"Session End:   {data.get('session_end', 'Unknown')}")
    console.print(f"Dropped Events: [yellow]{data.get('dropped_events', 0)}[/yellow]\n")
    
    # Render Events Table (cap at last 100 events for performance)
    events = data.get("events", [])
    if events:
        table = Table(title=f"Function Call Trace (Last {min(len(events), 100)} events)", show_header=True, header_style="bold magenta")
        table.add_column("Timestamp", style="dim", width=25)
        table.add_column("Type", width=12)
        table.add_column("Function", style="cyan")
        table.add_column("File:Line", style="green")
        table.add_column("Details", justify="left")
        
        # Only show the last 100 events to prevent terminal freezing
        for ev in events[-100:]:
            ev_type = ev.get("type", "")
            func = ev.get("function", "")
            file_line = f"{os.path.basename(ev.get('file', ''))}:{ev.get('line', '')}"
            ts = ev.get("timestamp", "")
            
            details = ""
            if ev_type == "call":
                details = str(ev.get("inputs", {}))
            elif ev_type == "return":
                details = str(ev.get("return_value", ""))
            elif ev_type == "exception_caught":
                details = f"[red]{ev.get('exception_type')}: {ev.get('exception_message')}[/red]"
                
            table.add_row(ts, ev_type, func, file_line, details)
            
        console.print(table)
    
    # Render Crash Diagnosis
    crash = data.get("crash")
    if crash:
        console.print("\n[bold red]💥 Crash Report[/bold red]")
        
        # Diagnosis Panel
        diagnosis_text = Text(crash.get("diagnosis", "No diagnosis available."), style="bold yellow")
        diagnosis_panel = Panel(diagnosis_text, title="AI/Heuristic Diagnosis", border_style="red")
        console.print(diagnosis_panel)
        
        # Variables Syntax View
        variables = crash.get("variables", {})
        vars_json = json.dumps(variables, indent=2)
        syntax = Syntax(vars_json, "json", theme="monokai", line_numbers=True)
        vars_panel = Panel(syntax, title="Local Variables at Crash", border_style="blue")
        console.print(vars_panel)
        
        # Traceback Panel
        tb = crash.get("traceback", "")
        tb_panel = Panel(tb, title="Traceback", border_style="red", style="dim")
        console.print(tb_panel)
