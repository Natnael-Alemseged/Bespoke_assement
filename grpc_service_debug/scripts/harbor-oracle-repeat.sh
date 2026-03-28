#!/usr/bin/env bash
# Run Harbor oracle N times; append summaries to jobs/oracle-reliability.txt
# Usage: ./scripts/harbor-oracle-repeat.sh [N]
# Run from grpc_service_debug/ (task root). Uses parent path for -p "."

set -euo pipefail

TASK_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PARENT="$(cd "$TASK_ROOT/.." && pwd)"
cd "$PARENT"

N="${1:-5}"
OUT="$TASK_ROOT/jobs/oracle-reliability.txt"

mkdir -p "$TASK_ROOT/jobs"
{
  echo "=== batch start $(date -u +%Y-%m-%dT%H:%M:%SZ) N=$N (task: grpc_service_debug) ==="
} >>"$OUT"

TASK_NAME="$(basename "$TASK_ROOT")"
for i in $(seq 1 "$N"); do
  echo "=== Oracle run $i $(date -u +%Y-%m-%dT%H:%M:%SZ) ===" >>"$OUT"
  harbor run -p "./$TASK_NAME" -a oracle -y -q 2>&1 | tee -a "$OUT" | tail -8
  echo "" >>"$OUT"
done

echo "Appended $N oracle runs to $OUT"
