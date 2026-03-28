#!/usr/bin/env bash
# terminus-2 + groq/moonshotai/kimi-k2-instruct-0905 + k=10 (difficulty validation).
# Run from grpc_service_debug/. Env file defaults to ../.env (parent of task folder).
#
# The take-home example uses -n 10 for speed. On Groq on_demand TPM limits, ten
# concurrent trials often hit RateLimitError. Default N_CONCURRENT=1 keeps k=10
# while staying under limits; override: N_CONCURRENT=10 ./scripts/harbor-terminus-k10.sh

set -euo pipefail

TASK_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PARENT="$(cd "$TASK_ROOT/.." && pwd)"
cd "$PARENT"

ENV_FILE="${1:-$PARENT/.env}"
if [[ ! -f "$ENV_FILE" ]]; then
  echo "Missing env file: $ENV_FILE" >&2
  echo "Create .env with GROQ_API_KEY=... in the parent directory (see take-home)." >&2
  exit 1
fi

N_CONCURRENT="${N_CONCURRENT:-1}"

TASK_NAME="$(basename "$TASK_ROOT")"
exec harbor run \
  -p "./$TASK_NAME" \
  -a terminus-2 \
  --model groq/moonshotai/kimi-k2-instruct-0905 \
  -k 10 \
  -n "$N_CONCURRENT" \
  -y \
  --env-file "$ENV_FILE"
