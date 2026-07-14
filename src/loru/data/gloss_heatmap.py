"""Gloss coverage heatmap CLI."""

from rich.console import Console
from rich.table import Table
from loru.config import SAMPLES_DIR
from loru.data.loader import list_sample_files
from loru.models.vocab import DEFAULT_GLOSS

console = Console()

def show_gloss_coverage():
    """Show which glosses have samples."""
    files = list_sample_files()
    existing = {f.stem for f in files}
    
    table = Table(title="Gloss Coverage")
    table.add_column("Gloss", style="cyan")
    table.add_column("Status", style="green")
    
    covered = 0
    for g in sorted(DEFAULT_GLOSS):
        has_sample = g in existing
        status = "✓" if has_sample else "✗"
        style = "green" if has_sample else "red"
        table.add_row(g, f"[{style}]{status}[/{style}]")
        if has_sample:
            covered += 1
    
    console.print(table)
    console.print(f"\nCoverage: {covered}/{len(DEFAULT_GLOSS)} ({covered*100//len(DEFAULT_GLOSS)}%)")
