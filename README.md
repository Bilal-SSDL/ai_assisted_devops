# VM Health Check Script

This repository contains a Bash script for Ubuntu VMs that checks health based on CPU, memory, and disk usage.

## File

- `vm_health_check.sh`: evaluates VM health using a `60%` utilization threshold.

## Health Rules

- VM is `healthy` only when all metrics are below `60%`.
- VM is `non-healthy` when any metric is greater than or equal to `60%`.
- Exactly `60%` is treated as `non-healthy`.

## Requirements

- Ubuntu Linux
- Bash
- Standard tools available by default on Ubuntu: `awk`, `free`, `df`, and `/proc/stat`

## Usage

Make executable (if needed):

```bash
chmod +x vm_health_check.sh
```

Run default mode (status only):

```bash
./vm_health_check.sh
```

Run explain mode (status + reason details):

```bash
./vm_health_check.sh explain
```

## Output Examples

Default mode:

```text
healthy
```

or

```text
non-healthy
```

Explain mode:

```text
health_status: non-healthy
cpu_utilization: 72%
memory_utilization: 58%
disk_utilization_root: 64%
reason: One or more metrics are at or above 60% utilization.
- CPU utilization is 72% (>= 60%)
- Disk utilization on / is 64% (>= 60%)
```

## Invalid Argument Behavior

Any argument other than `explain` is invalid:

```bash
./vm_health_check.sh something_else
```

Returns:
- usage message: `Usage: ./vm_health_check.sh [explain]`
- non-zero exit code (`1`)
