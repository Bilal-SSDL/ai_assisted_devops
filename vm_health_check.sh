#!/usr/bin/env bash

set -euo pipefail

THRESHOLD=86
MODE="${1:-}"

usage() {
  echo "Usage: $0 [explain]" >&2
}

if [[ -n "$MODE" && "$MODE" != "explain" ]]; then
  usage
  exit 1
fi

read_cpu_times() {
  local cpu_line
  cpu_line=$(awk '/^cpu / {print $2, $3, $4, $5, $6, $7, $8, $9, $10, $11}' /proc/stat)

  local user nice system idle iowait irq softirq steal guest guest_nice
  read -r user nice system idle iowait irq softirq steal guest guest_nice <<<"$cpu_line"

  local idle_all non_idle total
  idle_all=$((idle + iowait))
  non_idle=$((user + nice + system + irq + softirq + steal))
  total=$((idle_all + non_idle))

  echo "$idle_all $total"
}

read -r idle1 total1 <<<"$(read_cpu_times)"
sleep 1
read -r idle2 total2 <<<"$(read_cpu_times)"

total_diff=$((total2 - total1))
idle_diff=$((idle2 - idle1))

if (( total_diff <= 0 )); then
  cpu_used=0
else
  cpu_used=$(( (100 * (total_diff - idle_diff)) / total_diff ))
fi

mem_used=$(free | awk '/^Mem:/ {if ($2 == 0) print 0; else printf "%d", ($3 * 100) / $2}')
disk_used=$(df -P / | awk 'NR==2 {gsub("%","",$5); print $5}')

status="healthy"
reasons=()

if (( cpu_used >= THRESHOLD )); then
  status="non-healthy"
  reasons+=("CPU utilization is ${cpu_used}% (>= ${THRESHOLD}%)")
fi

if (( mem_used >= THRESHOLD )); then
  status="non-healthy"
  reasons+=("Memory utilization is ${mem_used}% (>= ${THRESHOLD}%)")
fi

if (( disk_used >= THRESHOLD )); then
  status="non-healthy"
  reasons+=("Disk utilization on / is ${disk_used}% (>= ${THRESHOLD}%)")
fi

if [[ "$MODE" == "explain" ]]; then
  echo "health_status: $status"
  echo "cpu_utilization: ${cpu_used}%"
  echo "memory_utilization: ${mem_used}%"
  echo "disk_utilization_root: ${disk_used}%"

  if [[ "$status" == "healthy" ]]; then
    echo "reason: All metrics are below ${THRESHOLD}% utilization."
  else
    echo "reason: One or more metrics are at or above ${THRESHOLD}% utilization."
    for reason in "${reasons[@]}"; do
      echo "- $reason"
    done
  fi
else
  echo "$status"
fi
