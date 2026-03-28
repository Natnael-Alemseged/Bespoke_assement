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

### Run 2026-03-28 (incomplete — job stopped after infrastructure errors)

| Field | Value |
|-------|--------|
| Date (UTC) | 2026-03-28 (start ~02:55 UTC) |
| Harbor job directory | `jobs/2026-03-28__02-55-43/` (repo root) |
| Agent | terminus-2 |
| Model | groq/moonshotai/kimi-k2-instruct-0905 |
| k (attempts) | 10 |
| n (concurrent trials) | 1 |
| Mean reward (from report) | *(job did not finish — aggregate `finished_at` was null when stopped)* |
| Errors (from report) | First completed trials: `RateLimitError`, `AgentSetupTimeoutError` (see below) |
| Notes | API key was valid; failures were **Groq TPM** (large single requests vs 10k TPM) and **terminus-2 setup** (tmux/asciinema install stalled until setup timeout). |

**Per-trial artifacts (under `jobs/2026-03-28__02-55-43/`):**

| Trial | Outcome |
|-------|---------|
| `grpc_service_debug__9eBXgff` | Agent ran, then failed with **Groq `RateLimitError`** (TPM ~10k limit; request ~9.8k tokens). |
| `grpc_service_debug__PG2xzWa` | **AgentSetupTimeoutError** after 360s — tmux/asciinema install inside the container did not finish in time. |

**Next steps for a clean k=10 report**

1. Run when Groq is not over capacity (`kimi-k2` status); see [groqstatus.com](https://groqstatus.com).
2. Prefer a **higher Groq tier** or **smaller TPM bursts** so kimi-k2 stays under your org’s TPM (or wait between attempts).
3. Keep **`-n 1`** to avoid parallel TPM spikes.
4. If setup keeps timing out, update Harbor and retry; pre-warm Docker so agent setup is faster.

**Template for a successful completion**

| Field | Value |
|-------|--------|
| Date (UTC) | |
| Harbor job directory | |
| Mean reward | |
| Errors | |

Oracle-only reliability is logged in [oracle-reliability.txt](./oracle-reliability.txt). This table is for the **terminus-2 / k=10 / Groq / kimi-k2** agent run.
