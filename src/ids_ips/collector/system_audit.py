from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List

import json
import platform
import psutil

from ids_ips.config import AuditConfig, ensure_output_dir


@dataclass
class SystemSnapshot:
    platform_system: str
    platform_release: str
    platform_version: str
    cpu_count_logical: int
    cpu_count_physical: int
    memory_total: int
    processes_count: int
    disk_count: int
    net_if_count: int
    tcp_conn_count: int
    udp_conn_count: int


def collect_system_snapshot() -> SystemSnapshot:
    """Собрать базовую информацию о системе (аналог части тестов Lynis)."""
    vm = psutil.virtual_memory()
    processes = list(psutil.process_iter(attrs=["pid"]))
    disks = psutil.disk_partitions(all=False)
    net_if = psutil.net_if_addrs()
    conns: List[psutil._common.sconn] = psutil.net_connections()

    tcp_conns = [c for c in conns if c.type == psutil.SOCK_STREAM]
    udp_conns = [c for c in conns if c.type == psutil.SOCK_DGRAM]

    return SystemSnapshot(
        platform_system=platform.system(),
        platform_release=platform.release(),
        platform_version=platform.version(),
        cpu_count_logical=psutil.cpu_count(logical=True) or 0,
        cpu_count_physical=psutil.cpu_count(logical=False) or 0,
        memory_total=int(vm.total),
        processes_count=len(processes),
        disk_count=len(disks),
        net_if_count=len(net_if),
        tcp_conn_count=len(tcp_conns),
        udp_conn_count=len(udp_conns),
    )


def run_basic_audit(cfg: AuditConfig) -> Path:
    """Запустить простой аудит и сохранить результаты в JSON.

    Возвращает путь к файлу с сырыми данными аудита, пригодными для
    последующего фичеринга и обучения моделей.
    """
    ensure_output_dir(cfg)
    snapshot = collect_system_snapshot()
    output_path = cfg.output_dir / "system_snapshot.json"

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(asdict(snapshot), f, ensure_ascii=False, indent=2)

    return output_path


def load_audit_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


