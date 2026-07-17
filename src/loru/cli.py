from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from loru import __version__
from loru.config import OUT_DIR, RUNS_DIR, SAMPLES_DIR
from loru.data.loader import list_sample_files, sequence_summary
from loru.data.stats import compute_sequence_stats, detect_outliers, print_stats_table, print_outliers_table, print_summary
from loru.data.wlasl import load_wlasl_manifest, write_wlasl_manifest
from loru.infer.pipeline import sign_to_voice
from loru.infer.text import gloss_to_sentence, multi_gloss_to_sentence, sign_to_text
from loru.models.vocab import DEFAULT_GLOSS
from loru.train.toy_train import train_toy

app = typer.Typer(
    help="Loru — sign-to-text and sign-to-voice (runnable offline demo).",
    no_args_is_help=True,
)
data_app = typer.Typer(help="Dataset helpers")
samples_app = typer.Typer(help="Browse local landmark samples")
infer_app = typer.Typer(help="Inference (sign→text / sign→voice)")
train_app = typer.Typer(help="Training")
eval_app = typer.Typer(help="Evaluation")
app.add_typer(data_app, name="data")
app.add_typer(samples_app, name="samples")
app.add_typer(infer_app, name="infer")
app.add_typer(train_app, name="train")
app.add_typer(eval_app, name="eval")
console = Console()


@app.command("version")
def version_cmd() -> None:
    console.print(f"Loru {__version__}")
    console.print(f"Demo gloss vocab ({len(DEFAULT_GLOSS)}): {', '.join(DEFAULT_GLOSS)}")





@data_app.command("stats")
def stats_cmd(
    method: str = typer.Option("iqr", help="Outlier detection method (iqr or zscore)"),
    threshold: float = typer.Option(1.5, help="Outlier threshold"),
    directory: Optional[str] = typer.Option(None, help="Custom samples directory"),
) -> None:
    """Report frame counts per sample and flag outliers."""
    from loru.config import SAMPLES_DIR
    
    dir_path = Path(directory) if directory else SAMPLES_DIR
    stats = compute_sequence_stats(dir_path)
    outliers = detect_outliers(stats, method=method, threshold=threshold)
    
    print_stats_table(stats)
    print_outliers_table(outliers)
    print_summary(stats, outliers)

@app.command("gui")
def gui_cmd() -> None:
    """Launch modern Qt desktop demo (pip install -e '.[gui]')."""
    from loru.gui.app import main as gui_main

    raise SystemExit(gui_main())


@app.command("demo")
def demo_cmd() -> None:
    """Run full offline demo: list samples, train, infer text+voice on hello."""
    files = list_sample_files()
    console.print(f"[cyan]samples[/cyan]={len(files)} dir={SAMPLES_DIR}")
    report = train_toy(epochs=2)
    console.print(f"[green]train accuracy[/green]={report['history'][-1]['accuracy']}")
    hello = SAMPLES_DIR / "hello.json"
    if not hello.exists() and files:
        hello = files[0]
    text = sign_to_text(hello)
    console.print_json(data=text)
    wav = OUT_DIR / "demo_hello.wav"
    voice = sign_to_voice(hello, wav)
    console.print(f"[green]voice[/green] {voice['audio_path']}")
    console.print("[bold]Demo complete — offline sign→text→voice works.[/bold]")


@infer_app.command("stream")
def infer_stream(
    glosses: str = typer.Option(
        "hello thanks",
        "--glosses",
        "-g",
        help="Space-separated gloss stream (continuous stub)",
    ),
) -> None:
    """Progressive multi-gloss sentence stream (scaffold for live recognition)."""
    from loru.infer.stream import stream_glosses

    parts = [g for g in glosses.replace(",", " ").split() if g.strip()]
    console.print_json(data=stream_glosses(parts))


@infer_app.command("extract")
def infer_extract(
    gloss: str = typer.Option("hello", "--gloss", "-g"),
    out: Path | None = typer.Option(None, "--out", "-o"),
    source: Path | None = typer.Option(None, "--source", "-s", exists=True, dir_okay=False),
    frames: int = typer.Option(8, "--frames", "-n", min=1, max=60),
) -> None:
    """Extract/write landmark sample JSON (MediaPipe if available, else synthetic)."""
    from loru.config import OUT_DIR
    from loru.infer.extract import extract_landmarks, write_extract

    payload = extract_landmarks(source, gloss=gloss, frames=frames)
    path = out or (OUT_DIR / f"extract_{gloss}.json")
    write_extract(payload, path)
    console.print(f"[green]extract[/green] {path} frames={len(payload.get('frames') or [])} via={payload.get('extractor')}")


@data_app.command("vocab")
def data_vocab() -> None:
    """List demo gloss vocabulary with indices."""
    table = Table(title=f"DEFAULT_GLOSS ({len(DEFAULT_GLOSS)})")
    table.add_column("#", justify="right")
    table.add_column("Gloss")
    for i, g in enumerate(DEFAULT_GLOSS):
        table.add_row(str(i), g)
    console.print(table)


@data_app.command("sentence")
def data_sentence(
    glosses: str = typer.Option(
        "hello thanks",
        "--glosses",
        "-g",
        help="Space-separated glosses → natural-language sentence",
    ),
) -> None:
    """Compose a sentence from multiple glosses (offline templates)."""
    parts = [g for g in glosses.replace(",", " ").split() if g.strip()]
    console.print_json(
        data={
            "glosses": parts,
            "sentence": multi_gloss_to_sentence(parts),
            "single": {g: gloss_to_sentence(g) for g in parts[:8]},
        }
    )


@data_app.command("coverage")
def data_coverage() -> None:
    """Which DEFAULT_GLOSS entries have bundled sample JSON."""
    files = {p.stem for p in list_sample_files()}
    table = Table(title="Gloss sample coverage")
    table.add_column("Gloss")
    table.add_column("Sample")
    have = 0
    for g in DEFAULT_GLOSS:
        ok = g in files
        if ok:
            have += 1
        table.add_row(g, "yes" if ok else "no")
    console.print(table)
    console.print(f"[dim]{have}/{len(DEFAULT_GLOSS)} glosses have samples[/dim]")


@data_app.command("wlasl-manifest")
def data_wlasl_manifest(
    index: Path = typer.Option(
        ...,
        "--index",
        "-i",
        exists=True,
        dir_okay=False,
        help="WLASL-style index JSON file.",
    ),
    samples_dir: Path | None = typer.Option(
        None,
        "--samples-dir",
        file_okay=False,
        help="Directory of local Loru sample JSON files to match by normalized gloss.",
    ),
    out: Path | None = typer.Option(
        None,
        "--out",
        "-o",
        help="Optional output path for the converted manifest JSON.",
    ),
) -> None:
    """Convert WLASL-style metadata into a Loru sequence manifest."""
    if out:
        manifest = write_wlasl_manifest(index, out, samples_dir=samples_dir)
        console.print(f"[green]WLASL manifest[/green] {out} entries={len(manifest)}")
        return

    console.print_json(data=load_wlasl_manifest(index, samples_dir=samples_dir))


@data_app.command("export-csv")
def data_export_csv(
    out: Path = typer.Option(None, "--out", "-o", help="Output CSV file path. Default: data/out/vocab_export.csv"),
) -> None:
    """Export gloss vocabulary as CSV with index and has_sample flag (for teachers)."""
    import csv

    from loru.config import OUT_DIR

    files = {p.stem for p in list_sample_files()}
    out_path = out or (OUT_DIR / "vocab_export.csv")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for i, g in enumerate(DEFAULT_GLOSS):
        has_sample = "true" if g in files else "false"
        rows.append({"index": str(i), "gloss": g, "has_sample": has_sample})
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["index", "gloss", "has_sample"])
        writer.writeheader()
        writer.writerows(rows)
    console.print(f"[green]CSV written[/green] → {out_path} ({len(rows)} rows)")


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


@samples_app.command("list")
def samples_list(
    gloss: str | None = typer.Option(
        None,
        "--gloss",
        "-g",
        help="Case-insensitive gloss substring to include.",
    ),
    directory: Path | None = typer.Option(
        None,
        "--directory",
        "-d",
        exists=True,
        file_okay=False,
        help="Custom sample directory. Defaults to data/samples.",
    ),
) -> None:
    """List samples with language and frame counts, optionally filtered by gloss."""
    query = gloss.strip().lower() if gloss else None
    rows = []
    for path in list_sample_files(directory):
        summary = sequence_summary(path)
        if query and query not in summary["gloss"]:
            continue
        rows.append((path, summary))

    root = directory or SAMPLES_DIR
    if not rows:
        detail = f" matching gloss '{gloss}'" if gloss else ""
        console.print(f"[yellow]No samples{detail} in {root}[/yellow]")
        raise typer.Exit()

    table = Table(title=f"Samples ({len(rows)})")
    table.add_column("File")
    table.add_column("Gloss")
    table.add_column("Language")
    table.add_column("Frames", justify="right")
    for path, summary in rows:
        table.add_row(
            path.name,
            summary["gloss"],
            summary["language"],
            str(summary["frames"]),
        )
    console.print(table)


@infer_app.command("demo")
def infer_demo(sign: str = typer.Option("hello", "--sign", "-s")) -> None:
    console.print(f"[cyan]gloss[/cyan]={sign}")
    console.print(f"[green]text[/green]={gloss_to_sentence(sign)}")


@infer_app.command("text")
def infer_text(
    sequence: Path = typer.Option(..., "--sequence", "-i", exists=True, dir_okay=False),
) -> None:
    console.print_json(data=sign_to_text(sequence))


@infer_app.command("voice")
def infer_voice(
    sequence: Path = typer.Option(..., "--sequence", "-i", exists=True, dir_okay=False),
    out: Path = typer.Option(None, "--out", "-o"),
) -> None:
    out_path = out or (OUT_DIR / f"{sequence.stem}.wav")
    console.print_json(data=sign_to_voice(sequence, out_path))


@infer_app.command("sentence")
def infer_sentence(
    gloss: list[str] = typer.Option(..., "--gloss", "-g", help="Repeat for multi-gloss"),
) -> None:
    text = multi_gloss_to_sentence(gloss)
    console.print_json(data={"glosses": gloss, "text": text})


@eval_app.command("toy")
def eval_toy() -> None:
    files = list_sample_files()
    if not files:
        console.print("[yellow]No samples[/yellow]")
        raise typer.Exit(1)
    hits = 0
    table = Table(title="Eval toy")
    table.add_column("File")
    table.add_column("True")
    table.add_column("Pred")
    table.add_column("Conf")
    table.add_column("OK")
    for path in files:
        r = sign_to_text(path)
        ok = r["predicted_gloss"] == r["true_gloss"]
        if ok:
            hits += 1
        table.add_row(
            path.name,
            r["true_gloss"],
            r["predicted_gloss"],
            str(r["confidence"]),
            "✓" if ok else "✗",
        )
    console.print(table)
    acc = hits / len(files)
    console.print(f"accuracy={acc:.3f} ({hits}/{len(files)})")
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    report = {"accuracy": round(acc, 4), "hits": hits, "n": len(files)}
    (RUNS_DIR / "eval_toy.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if acc < 0.8:
        raise typer.Exit(1)


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


@app.command("serve")
def serve_cmd(
    host: str = typer.Option("127.0.0.1", "--host"),
    port: int = typer.Option(8766, "--port", min=1, max=65535),
) -> None:
    """Run FastAPI (pip install -e '.[api]')."""
    try:
        import uvicorn
    except ImportError as exc:
        console.print('[red]Install:[/red] pip install -e ".[api]"')
        raise typer.Exit(1) from exc
    console.print(f"Serving http://{host}:{port}/health")
    uvicorn.run("loru.api.app:app", host=host, port=port, log_level="info")


if __name__ == "__main__":
    app()
