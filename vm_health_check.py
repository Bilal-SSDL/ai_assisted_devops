#!/usr/bin/env python3
"""
Ubuntu VM health check based on CPU, memory, and disk utilization.

Health rule:
- healthy: all metrics are below THRESHOLD
- non-healthy: any metric is greater than or equal to THRESHOLD
"""

from __future__ import annotations

import argparse
import shutil
import time
from dataclasses import dataclass

THRESHOLD = 86


@dataclass(frozen=True)
class Metrics:
    cpu_utilization: int
    memory_utilization: int
    disk_utilization_root: int


def _read_cpu_times() -> tuple[int, int]:
    """
    Read aggregate CPU times from /proc/stat.

    Returns:
        (idle_all, total)
    """
    with open("/proc/stat", "r", encoding="utf-8") as file:
        for line in file:
            if line.startswith("cpu "):
                values = [int(value) for value in line.split()[1:11]]
                break
        else:
            raise RuntimeError("Unable to read aggregate CPU data from /proc/stat.")

    user, nice, system, idle, iowait, irq, softirq, steal, _guest, _guest_nice = values
    idle_all = idle + iowait
    non_idle = user + nice + system + irq + softirq + steal
    total = idle_all + non_idle
    return idle_all, total


def get_cpu_utilization_percent(interval_seconds: float = 1.0) -> int:
    idle_1, total_1 = _read_cpu_times()
    time.sleep(interval_seconds)
    idle_2, total_2 = _read_cpu_times()

    total_diff = total_2 - total_1
    idle_diff = idle_2 - idle_1

    if total_diff <= 0:
        return 0

    used_percent = (100 * (total_diff - idle_diff)) // total_diff
    return max(0, min(100, used_percent))


def get_memory_utilization_percent() -> int:
    total_kb = 0
    available_kb = 0

    with open("/proc/meminfo", "r", encoding="utf-8") as file:
        for line in file:
            if line.startswith("MemTotal:"):
                total_kb = int(line.split()[1])
            elif line.startswith("MemAvailable:"):
                available_kb = int(line.split()[1])

            if total_kb and available_kb:
                break

    if total_kb <= 0:
        return 0

    used_kb = max(0, total_kb - available_kb)
    return (100 * used_kb) // total_kb


def get_disk_utilization_percent(path: str = "/") -> int:
    usage = shutil.disk_usage(path)
    if usage.total <= 0:
        return 0
    return (100 * usage.used) // usage.total


def collect_metrics() -> Metrics:
    return Metrics(
        cpu_utilization=get_cpu_utilization_percent(),
        memory_utilization=get_memory_utilization_percent(),
        disk_utilization_root=get_disk_utilization_percent("/"),
    )


def evaluate_health(metrics: Metrics, threshold: int) -> tuple[str, list[str]]:
    status = "healthy"
    reasons: list[str] = []

    if metrics.cpu_utilization >= threshold:
        status = "non-healthy"
        reasons.append(
            f"CPU utilization is {metrics.cpu_utilization}% (>= {threshold}%)"
        )

    if metrics.memory_utilization >= threshold:
        status = "non-healthy"
        reasons.append(
            f"Memory utilization is {metrics.memory_utilization}% (>= {threshold}%)"
        )

    if metrics.disk_utilization_root >= threshold:
        status = "non-healthy"
        reasons.append(
            f"Disk utilization on / is {metrics.disk_utilization_root}% (>= {threshold}%)"
        )

    return status, reasons


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Check Ubuntu VM health from CPU, memory, and disk utilization."
    )
    parser.add_argument(
        "mode",
        nargs="?",
        choices=["explain"],
        help="Use 'explain' to print detailed reasons.",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    metrics = collect_metrics()
    status, reasons = evaluate_health(metrics, THRESHOLD)

    if args.mode == "explain":
        print(f"health_status: {status}")
        print(f"cpu_utilization: {metrics.cpu_utilization}%")
        print(f"memory_utilization: {metrics.memory_utilization}%")
        print(f"disk_utilization_root: {metrics.disk_utilization_root}%")

        if status == "healthy":
            print(f"reason: All metrics are below {THRESHOLD}% utilization.")
        else:
            print(f"reason: One or more metrics are at or above {THRESHOLD}% utilization.")
            for reason in reasons:
                print(f"- {reason}")
    else:
        print(status)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
