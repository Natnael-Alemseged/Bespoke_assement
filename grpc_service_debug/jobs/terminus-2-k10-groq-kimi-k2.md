# Terminus-2 — Groq / kimi-k2 — k=10 evidence checklist

## Command (take-home requirement)

From the **parent** directory of `grpc_service_debug/`:

```bash
harbor run \
  -p "./grpc_service_debug" \
  -a terminus-2 \
  --model groq/moonshotai/kimi-k2-instruct-0905 \
  -k 10 \
  -n 1 \
  -y \
  --env-file .env
```

Prerequisites: `GROQ_API_KEY` in `.env`, Docker running, Harbor installed.

**Note:** The take-home uses `-n 10` for throughput; on Groq free/on_demand TPM limits, use **`-n 1`** so concurrent trials do not trip `RateLimitError`. **`-k 10`** is unchanged (required attempts).

Or use `./scripts/harbor-terminus-k10.sh` from inside `grpc_service_debug/` (defaults to `-n 1`; set `N_CONCURRENT=10` to match the take-home example if your tier allows it).

## After the run

1. Copy Harbor’s **final summary** (mean reward, errors).
2. Note the job path (e.g. parent `jobs/<timestamp>/result.json`).
3. Fill the table below.

## Results

### Run 2026-03-28T15:42 UTC — completed, infrastructure-blocked

| Field | Value |
|-------|--------|
| Date (UTC) | 2026-03-28 ~12:42 UTC |
| Harbor job directory | `jobs/2026-03-28__15-42-56/` (repo root) |
| Agent | terminus-2 (moonshotai-kimi-k2-instruct-0905) |
| Model | groq/moonshotai/kimi-k2-instruct-0905 |
| k (attempts) | 10 |
| n (concurrent trials) | 1 |
| Trials completed | 1 |
| Errors | 9 (`RateLimitError`) |
| Mean reward (Harbor report) | 0.000 |
| Reward distribution | reward=0.0 × 1 |
| Exception distribution | RateLimitError × 9 |

**Root cause:** Groq `on_demand` service tier caps kimi-k2 at **10,000 TPM**. Each terminus-2 agent step requests **11,000–11,500 tokens**, permanently exceeding the per-minute limit. Only 1 of 10 trials ran to agent completion (reward=0.0 — agent did not solve the task); the remaining 9 were killed by `RateLimitError` before the agent could act.

**This is a Groq tier constraint, not a task/oracle problem.** The oracle runs at 1.000 (6/6). A valid difficulty run requires **Groq Dev tier** (higher TPM) or a model with lower per-request token usage.

**Per-trial summary:**

| Outcome | Count | Cause |
|---------|-------|-------|
| Completed (reward=0.0) | 1 | Agent ran but did not fix all bugs |
| Errored | 9 | `RateLimitError`: request size > 10k TPM cap |

**To obtain a valid k=10 run:**
1. Upgrade Groq to **Dev tier** (removes the 10k TPM cap) — costs are reimbursable per take-home spec.
2. Re-run: `harbor run -p "./grpc_service_debug" -a terminus-2 --model groq/moonshotai/kimi-k2-instruct-0905 -k 10 -n 1 -y --env-file .env`
3. Paste Harbor’s final summary table in this file.

Oracle-only reliability is logged in [oracle-reliability.txt](./oracle-reliability.txt). This table is for the **terminus-2 / k=10 / Groq / kimi-k2** agent run.
