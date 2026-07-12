from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from loru import __version__
from loru.config import OUT_DIR, SAMPLES_DIR
from loru.data.loader import list_sample_files, sequence_summary
from loru.infer.pipeline import sign_to_voice
from loru.infer.text import gloss_to_sentence, sign_to_text
from loru.models.vocab import DEFAULT_GLOSS
from loru.train.toy_train import train_toy

app = typer.Typer(help="Loru — sign-to-text and sign-to-voice training toolkit.", no_args_is_help=True)
data_app = typer.Typer(help="Dataset helpers")
infer_app = typer.Typer(help="Inference (sign→text / sign→voice)")
train_app = typer.Typer(help="Training")
app.add_typer(data_app, name="data")
app.add_typer(infer_app, name="infer")
app.add_typer(train_app, name="train")
console = Console()


@app.command("version")
def version_cmd() -> None:
    console.print(f"Loru {__version__}")
    console.print(f"Demo gloss vocab ({len(DEFAULT_GLOSS)}): {', '.join(DEFAULT_GLOSS)}")


@data_app.command("list")
def data_list() -> None:
    files = list_sample_files()
    if not files:
        console.print(f"[yellow]No samples in {SAMPLES_DIR}[/yellow]")
        raise typer.Exit()
    table = Table(title=f"Samples ({len(files)})")
    table.add_column("File")
    table.add_column("Gloss")
    table.add_column("Frames")
    for path in files:
        summary = sequence_summary(path)
        table.add_row(path.name, summary["gloss"], str(summary["frames"]))
    console.print(table)


@infer_app.command("demo")
def infer_demo(sign: str = typer.Option("hello", "--sign", "-s")) -> None:
    """Print natural language for a gloss without video."""
    console.print(f"[cyan]gloss[/cyan]={sign}")
    console.print(f"[green]text[/green]={gloss_to_sentence(sign)}")


@infer_app.command("text")
def infer_text(
    sequence: Path = typer.Option(..., "--sequence", "-i", exists=True, dir_okay=False),
) -> None:
    result = sign_to_text(sequence)
    console.print_json(data=result)


@infer_app.command("voice")
def infer_voice(
    sequence: Path = typer.Option(..., "--sequence", "-i", exists=True, dir_okay=False),
    out: Path = typer.Option(None, "--out", "-o"),
) -> None:
    out_path = out or (OUT_DIR / f"{sequence.stem}.wav")
    result = sign_to_voice(sequence, out_path)
    console.print_json(data=result)


@train_app.command("toy")
def train_toy_cmd(epochs: int = typer.Option(3, "--epochs", "-e", min=1, max=50)) -> None:
    report = train_toy(epochs=epochs)
    console.print(f"[green]Training complete[/green] accuracy={report['history'][-1]['accuracy']}")
    console.print(f"Report: {report['report_path']}")


@train_app.command("report")
def train_report() -> None:
    path = Path("data/runs/toy_train_report.json")
    if not path.exists():
        console.print("[yellow]No report yet. Run: loru train toy[/yellow]")
        raise typer.Exit(code=1)
    console.print(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    app()
