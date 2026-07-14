from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import numpy as np
from rich.console import Console
from rich.table import Table
from rich import box

from loru.config import SAMPLES_DIR
from loru.data.loader import list_sample_files, load_sequence


console = Console()


def compute_sequence_stats(directory: Optional[Path] = None) -> list[dict]:
    """Compute frame count statistics for all sequences."""
    files = list_sample_files(directory)
    stats = []
    
    for path in files:
        try:
            gloss, frames = load_sequence(path)
            frame_count = int(frames.shape[0]) if frames.ndim >= 1 else 0
            feature_dim = int(frames.reshape(frames.shape[0], -1).shape[1]) if frames.size else 0
            
            stats.append({
                'gloss': gloss,
                'path': path.name,
                'frame_count': frame_count,
                'feature_dim': feature_dim,
                'mean_magnitude': float(np.mean(np.abs(frames))) if frames.size else 0.0,
                'max_magnitude': float(np.max(np.abs(frames))) if frames.size else 0.0,
            })
        except Exception as e:
            console.print(f"[red]Error loading {path.name}: {e}[/red]")
    
    return stats


def detect_outliers(stats: list[dict], method: str = 'iqr', threshold: float = 1.5) -> list[dict]:
    """Detect outliers in frame counts using IQR or z-score method."""
    if not stats:
        return []
    
    frame_counts = np.array([s['frame_count'] for s in stats])
    
    if method == 'iqr':
        q1 = np.percentile(frame_counts, 25)
        q3 = np.percentile(frame_counts, 75)
        iqr = q3 - q1
        lower_bound = q1 - threshold * iqr
        upper_bound = q3 + threshold * iqr
        outliers = [s for s in stats if s['frame_count'] < lower_bound or s['frame_count'] > upper_bound]
    elif method == 'zscore':
        mean = np.mean(frame_counts)
        std = np.std(frame_counts)
        if std == 0:
            return []
        outliers = [s for s in stats if abs((s['frame_count'] - mean) / std) > threshold]
    else:
        raise ValueError(f"Unknown method: {method}")
    
    return outliers


def print_stats_table(stats: list[dict]) -> None:
    """Print statistics as a formatted table."""
    table = Table(title="Sequence Statistics", box=box.ROUNDED)
    table.add_column("Gloss", style="cyan")
    table.add_column("Frames", justify="right", style="green")
    table.add_column("Features", justify="right")
    table.add_column("Mean Mag", justify="right")
    table.add_column("Max Mag", justify="right")
    
    for s in sorted(stats, key=lambda x: x['frame_count'], reverse=True):
        table.add_row(
            s['gloss'],
            str(s['frame_count']),
            str(s['feature_dim']),
            f"{s['mean_magnitude']:.4f}",
            f"{s['max_magnitude']:.4f}",
        )
    
    console.print(table)


def print_outliers_table(outliers: list[dict]) -> None:
    """Print outliers as a formatted table."""
    if not outliers:
        console.print("[green]No outliers detected.[/green]")
        return
    
    table = Table(title="Outliers Detected", box=box.ROUNDED, style="red")
    table.add_column("Gloss", style="cyan")
    table.add_column("Frames", justify="right", style="yellow")
    table.add_column("Path", style="dim")
    
    for s in outliers:
        table.add_row(s['gloss'], str(s['frame_count']), s['path'])
    
    console.print(table)


def print_summary(stats: list[dict], outliers: list[dict]) -> None:
    """Print summary statistics."""
    if not stats:
        console.print("[red]No sequences found.[/red]")
        return
    
    frame_counts = [s['frame_count'] for s in stats]
    
    console.print("
[bold]Summary Statistics[/bold]")
    console.print(f"  Total sequences: {len(stats)}")
    console.print(f"  Frame count range: {min(frame_counts)} - {max(frame_counts)}")
    console.print(f"  Mean frames: {np.mean(frame_counts):.1f}")
    console.print(f"  Std frames: {np.std(frame_counts):.1f}")
    console.print(f"  Median frames: {np.median(frame_counts):.1f}")
    console.print(f"  Outliers detected: {len(outliers)}")
