import logging
from pathlib import Path


def setup_logging(log_dir: Path) -> None:
    """Простейшая настройка логгера в файл и на консоль."""
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "ids_ips.log"

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )


