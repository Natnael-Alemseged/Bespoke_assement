# `grpc_service_debug` — Terminal Bench 2.0 task

Debug and fix a broken Python **gRPC** inventory microservice so it passes the verifier. Intended difficulty: **hard** (multi-bug, cross-RPC reasoning); golden path is validated with **Harbor oracle**.

## Layout (submission)

| Path | Role |
|------|------|
| `task.toml` | Harbor task config (`environment.runtime.python = "3.12"`) |
| `instruction.md` | Agent-facing goal and requirements |
| `environment/` | Docker image contents copied to `/app/` (no tests/solution here) |
| `solution/solve.sh` | Oracle / human fix script |
| `tests/test_outputs.py` | Verifier (pytest); not copied into the runtime image |

## Verify locally

From the **parent** of this directory (the folder that contains `grpc_service_debug/`):

```bash
harbor run -p "./grpc_service_debug" -a oracle -y
```

Agent / difficulty validation (Groq + kimi-k2) is documented under [`jobs/EVIDENCE.md`](jobs/EVIDENCE.md).

## Instruction ↔ tests (QC)

| `instruction.md` requirement | Covered by (behavioral) |
|------------------------------|-------------------------|
| Correct `CheckInventory` stock / `available` for all catalogue rows | `test_check_inventory_*`, `test_check_inventory_all_initial_values` |
| `ReserveInventory` succeeds when quantity ≤ stock; `remaining_stock` correct | `test_reserve_partial_*`, `test_reserve_exact_*`, `test_reserve_decrements_*`, `test_sequential_reservations_*` |
| `ReserveInventory` → `RESOURCE_EXHAUSTED` when quantity > stock | `test_reserve_over_stock_*`, `test_reserve_zero_stock_*` |
| `ListProducts` returns all products, names, stock without error | `test_list_products_*` |
| Independent inventory per servicer instance | `test_instances_have_independent_inventory` |

The five rows above are the five numbered requirements in `instruction.md` only. (Input-validation branches in `server.py` are unchanged by the bugfix and are not listed as verifier targets.)

## Zip for the Bespoke form

Zip **this folder** (`grpc_service_debug/`) so it contains the table above. Do not put verifier tests inside `environment/`.
