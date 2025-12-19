from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class AuditConfig:
    """Базовая конфигурация аудита."""

    output_dir: Path = field(
        default_factory=lambda: Path.cwd() / "artifacts"
    )
    collect_system_info: bool = True
    collect_processes: bool = True
    collect_network: bool = False  # можно включить позже


def ensure_output_dir(cfg: AuditConfig) -> None:
    cfg.output_dir.mkdir(parents=True, exist_ok=True)


