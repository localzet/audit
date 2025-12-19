from __future__ import annotations

from pathlib import Path
from typing import Dict, Any

import pandas as pd

from ids_ips.collector.system_audit import load_audit_json


def extract_basic_features(audit_path: Path) -> pd.DataFrame:
    """Преобразовать JSON‑аудит в табличные фичи для ML.

    Сейчас это 1 строка с агрегатами, но можно расширять:
    - добавлять соотношения (процессы/CPU, память/CPU и т.п.),
    - кодировать категориальные поля (тип ОС) one-hot и др.
    """
    raw: Dict[str, Any] = load_audit_json(audit_path)
    df = pd.DataFrame([raw])
    return df


