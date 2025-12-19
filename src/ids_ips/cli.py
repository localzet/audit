from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from ids_ips.config import AuditConfig
from ids_ips.collector.system_audit import run_basic_audit
from ids_ips.features.basic_features import extract_basic_features
from ids_ips.models.baseline import BaselineAnomalyModel

app = typer.Typer(help="IDS/IPS ML Audit Framework (Lynis-like)")
console = Console()


@app.command()
def audit(
    target: str = typer.Argument(
        "system",
        help="Что аудитим (пока поддерживается только 'system').",
    ),
    output_dir: Path = typer.Option(
        Path("artifacts"),
        "--output-dir",
        "-o",
        help="Директория для сохранения артефактов аудита.",
    ),
):
    """Запустить базовый аудит системы (аналог `lynis audit system`)."""
    if target != "system":
        typer.secho("Поддерживается только 'system' на данном этапе.", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    cfg = AuditConfig(output_dir=output_dir)

    console.rule("[bold cyan]System audit")
    audit_path = run_basic_audit(cfg)
    console.print(f"[green]Аудит завершён.[/green] JSON: {audit_path}")


@app.command()
def train_baseline(
    data_dir: Path = typer.Option(
        Path("artifacts"),
        "--data-dir",
        help="Директория с JSON-аудитами (пока ожидается один файл).",
    ),
    model_path: Path = typer.Option(
        Path("artifacts") / "models" / "baseline_iforest.joblib",
        "--model-path",
        help="Куда сохранить обученную модель.",
    ),
):
    """Обучить простую baseline-модель по собранным аудитам."""
    json_path = data_dir / "system_snapshot.json"
    if not json_path.exists():
        typer.secho(f"Файл аудита не найден: {json_path}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    df = extract_basic_features(json_path)
    model = BaselineAnomalyModel().fit(df)
    model.save(model_path)
    console.print(f"[green]Модель сохранена:[/green] {model_path}")


@app.command()
def score(
    model_path: Path = typer.Option(
        Path("artifacts") / "models" / "baseline_iforest.joblib",
        "--model-path",
        help="Путь к сохранённой модели.",
    ),
    data_dir: Path = typer.Option(
        Path("artifacts"),
        "--data-dir",
        help="Директория с JSON-аудитами.",
    ),
):
    """Оценить текущий аудит с помощью baseline-модели."""
    json_path = data_dir / "system_snapshot.json"
    if not json_path.exists():
        typer.secho(f"Файл аудита не найден: {json_path}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    if not model_path.exists():
        typer.secho(f"Модель не найдена: {model_path}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    df = extract_basic_features(json_path)
    model = BaselineAnomalyModel.load(model_path)

    scores = model.score_samples(df)
    labels = model.predict_labels(df)

    table = Table(title="Baseline anomaly scoring")
    table.add_column("sample_id")
    table.add_column("score", justify="right")
    table.add_column("label", justify="center")

    for i, (s, l) in enumerate(zip(scores, labels)):
        table.add_row(str(i), f"{s:.4f}", "ANOMALY" if l == -1 else "NORMAL")

    console.print(table)


def main():
    app()


if __name__ == "__main__":
    main()


