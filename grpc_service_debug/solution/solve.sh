#!/usr/bin/env bash
# Golden solution: fix all three bugs in /app/server.py

set -euo pipefail

SERVER="/app/server.py"

# ── Fix 1 ─────────────────────────────────────────────────────────────────────
# ReserveInventory uses strict greater-than (>) so a reservation for exactly
# the remaining quantity is incorrectly rejected.
# Correct the comparison to greater-than-or-equal (>=).
grep -q 'if current_stock > quantity:' "$SERVER" \
  || { echo "Fix 1: pattern not found in $SERVER"; exit 1; }
sed -i 's/if current_stock > quantity:/if current_stock >= quantity:/' "$SERVER"

# ── Fix 2 ─────────────────────────────────────────────────────────────────────
# ListProducts reads data["qty"] but the inventory dict stores the count under
# the key "stock", causing a KeyError on every call to ListProducts.
grep -q 'stock=data\["qty"\]' "$SERVER" \
  || { echo "Fix 2: pattern not found in $SERVER"; exit 1; }
sed -i 's/stock=data\["qty"\]/stock=data["stock"]/' "$SERVER"

# ── Fix 3 ─────────────────────────────────────────────────────────────────────
# InventoryServicer.__init__ assigns the module-level INITIAL_INVENTORY dict
# directly to self.inventory (a reference), so all instances share the same
# underlying object.  Replace with a per-instance deep copy.
python3 - <<'PYEOF'
path = "/app/server.py"
with open(path) as f:
    src = f.read()

old = "        self.inventory = INITIAL_INVENTORY"
new = "        self.inventory = {k: dict(v) for k, v in INITIAL_INVENTORY.items()}"

if old not in src:
    raise SystemExit(f"Pattern not found in {path}:\n  {old!r}")

src = src.replace(old, new, 1)

with open(path, "w") as f:
    f.write(src)

print("Fix 3 applied.")
PYEOF

echo "All 3 bugs fixed in $SERVER."
