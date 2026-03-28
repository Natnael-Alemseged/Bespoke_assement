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

### Run 2026-03-28T16:30 UTC — **VALID k=10 run (paid tier)**

| Field | Value |
|-------|--------|
| Date (UTC) | 2026-03-28 16:30–16:50 UTC |
| Harbor job directory | `jobs/2026-03-28__16-30-13/` (repo root) |
| Agent | terminus-2 (moonshotai-kimi-k2-instruct-0905) |
| Model | groq/moonshotai/kimi-k2-instruct-0905 |
| k (attempts) | 10 |
| n (concurrent trials) | 2 |
| Trials completed | 10 |
| Errors | 1 (`AgentTimeoutError`) |
| **Mean reward** | **0.200** |
| Reward distribution | reward=1.0 × 2, reward=0.0 × 8 |
| Exception distribution | AgentTimeoutError × 1 (within the 8 failures) |

**Success rate: 0.2 — within the required target band (> 0.0 and < 0.7). ✓**

The agent solved the task on 2 of 10 attempts. The remaining 8 either timed out or failed to identify and fix all three bugs. This confirms the task is **hard but solvable**.

**Per-trial summary:**

| Outcome | Count | Notes |
|---------|-------|-------|
| reward = 1.0 | 2 | Agent found and fixed all 3 bugs |
| reward = 0.0 | 8 | Agent did not fix all bugs (1 also hit AgentTimeoutError) |

Oracle-only reliability is logged in [oracle-reliability.txt](./oracle-reliability.txt). This table is for the **terminus-2 / k=10 / Groq / kimi-k2** agent run.
