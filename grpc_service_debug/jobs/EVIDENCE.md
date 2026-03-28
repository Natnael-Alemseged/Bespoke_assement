# Difficulty and reliability evidence — `grpc_service_debug`

Aligned with the Bespoke take-home: **oracle** plus **terminus-2** with **Groq** `moonshotai/kimi-k2-instruct-0905` and **k=10** attempts.

A **requirement ↔ test mapping** for graders is in [`../README.md`](../README.md) (QC section).

## 1. Oracle (golden solution) — repeated green runs

The verifier runs `solution/solve.sh` and `tests/test_outputs.py`.

- **Log:** [oracle-reliability.txt](./oracle-reliability.txt) — five consecutive oracle runs (see file), each **Mean reward 1.000**, **Errors 0**.

**One-shot check** (from the **parent** of this task folder, i.e. where `grpc_service_debug/` lives):

```bash
harbor run -p "./grpc_service_debug" -a oracle -y
```

Harbor writes large artifacts under the parent directory’s `jobs/<timestamp>/` (repository root `./jobs/` in a typical layout).

## 2. Terminus-2 — required command (k=10, Groq, kimi-k2)

From the **parent** of `grpc_service_debug/` (same as above):

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

Put `GROQ_API_KEY` in `.env` per the take-home document.

**Concurrency (`-n`):** The take-home example uses `-n 10` to finish faster. With Groq **on_demand** TPM caps for `kimi-k2`, ten concurrent trials often exhaust the per-minute token budget and return `RateLimitError`. Use **`-n 1`** (or `2`) for reliable runs while keeping **`-k 10`**, which is what matters for difficulty validation. You can still try `-n 10` on a higher Groq tier or after spacing runs.

**Identifiers for graders**

| Setting | Value |
|--------|--------|
| Agent | `terminus-2` |
| Model | `groq/moonshotai/kimi-k2-instruct-0905` |
| k | 10 |
| n | 1 (recommended on standard Groq TPM; take-home example shows 10) |

Record Harbor’s printed summary in [terminus-2-k10-groq-kimi-k2.md](./terminus-2-k10-groq-kimi-k2.md).

**Alternative:** from **inside** `grpc_service_debug/`, run `./scripts/harbor-terminus-k10.sh` (expects `../.env` by default) or:

```bash
cd grpc_service_debug
harbor run -p "." -a terminus-2 --model groq/moonshotai/kimi-k2-instruct-0905 -k 10 -n 1 -y --env-file ../.env
```

## 3. Target success band

Per take-home: average agent success rate should be **> 0.0** and **< 0.7** (hard but solvable).

## 4. Raw job directories

Keep the Harbor output directory for your **terminus-2 k=10** run if graders request full logs; it is usually under `./jobs/<timestamp>/` relative to where you ran the command.

## 5. Terminus-2 k=10 result — 2026-03-28 (valid run, paid Groq tier)

| Metric | Value |
|--------|-------|
| Mean reward | **0.200** |
| Trials | 10 |
| Errors | 1 (AgentTimeoutError) |
| reward = 1.0 | 2 trials |
| reward = 0.0 | 8 trials |
| Job directory | `jobs/2026-03-28__16-30-13/` (repo root) |

**Success rate 0.2 — confirmed within target band (> 0.0 and < 0.7). Task is hard but solvable. ✓**

Full per-trial breakdown in [terminus-2-k10-groq-kimi-k2.md](./terminus-2-k10-groq-kimi-k2.md).
