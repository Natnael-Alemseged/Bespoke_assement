"""
Functional tests for the Inventory Management gRPC Service.

Tests instantiate InventoryServicer directly (unit-test style) so no live
gRPC server is required.  A lightweight MockContext captures status codes and
detail messages set by the servicer.

Required packages (grpcio, protobuf) are installed at the top of this module
so they are available inside the uvx test environment.
"""

import subprocess
import sys

# ---------------------------------------------------------------------------
# Bootstrap: install gRPC + protobuf into the active test environment before
# any imports that depend on them.
# test.sh installs uv at ~/.local/bin/uv; use it to inject packages into the
# current Python interpreter (the uvx venv that has no pip).
# ---------------------------------------------------------------------------
import os as _os

_uv = _os.path.expanduser("~/.local/bin/uv")
subprocess.run(
    [
        _uv, "pip", "install",
        "--python", sys.executable,
        "--quiet",
        "grpcio==1.60.0",
        "protobuf==4.25.0",
    ],
    check=True,
)

# Make the app directory importable so server.py and the generated stubs can
# be imported as top-level modules.
sys.path.insert(0, "/app")

# ---------------------------------------------------------------------------
# Imports (must come after path and package setup above)
# ---------------------------------------------------------------------------
import grpc                          # noqa: E402
import inventory_pb2                 # noqa: E402
import inventory_pb2_grpc            # noqa: E402
from server import InventoryServicer  # noqa: E402


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class MockContext:
    """Minimal stand-in for grpc.ServicerContext used in unit tests."""

    def __init__(self):
        self._code = grpc.StatusCode.OK
        self._details = ""

    def set_code(self, code: grpc.StatusCode) -> None:
        self._code = code

    def set_details(self, details: str) -> None:
        self._details = details

    def is_active(self) -> bool:
        return True


def make_servicer() -> InventoryServicer:
    """Return a freshly initialised servicer with the default inventory."""
    return InventoryServicer()


# ===========================================================================
# CheckInventory tests
# ===========================================================================

def test_check_inventory_laptop_stock():
    """PROD-001 (Laptop) should report stock=10, available=True."""
    s = make_servicer()
    ctx = MockContext()
    r = s.CheckInventory(inventory_pb2.CheckRequest(product_id="PROD-001"), ctx)
    assert ctx._code == grpc.StatusCode.OK
    assert r.product_id == "PROD-001"
    assert r.stock == 10
    assert r.available is True


def test_check_inventory_out_of_stock():
    """PROD-005 (Headphones) has stock=0 and must be marked available=False."""
    s = make_servicer()
    ctx = MockContext()
    r = s.CheckInventory(inventory_pb2.CheckRequest(product_id="PROD-005"), ctx)
    assert ctx._code == grpc.StatusCode.OK
    assert r.stock == 0
    assert r.available is False


def test_check_inventory_not_found():
    """Unknown product IDs must return NOT_FOUND."""
    s = make_servicer()
    ctx = MockContext()
    s.CheckInventory(inventory_pb2.CheckRequest(product_id="UNKNOWN-999"), ctx)
    assert ctx._code == grpc.StatusCode.NOT_FOUND


def test_check_inventory_all_initial_values():
    """CheckInventory must return the correct initial stock for every product."""
    expected = {
        "PROD-001": 10,
        "PROD-002": 25,
        "PROD-003": 15,
        "PROD-004":  5,
        "PROD-005":  0,
    }
    s = make_servicer()
    for pid, want in expected.items():
        ctx = MockContext()
        r = s.CheckInventory(inventory_pb2.CheckRequest(product_id=pid), ctx)
        assert r.stock == want, (
            f"{pid}: expected stock={want}, got stock={r.stock}"
        )


# ===========================================================================
# ReserveInventory tests
# ===========================================================================

def test_reserve_partial_quantity_succeeds():
    """Reserving fewer units than available stock must succeed."""
    s = make_servicer()
    ctx = MockContext()
    r = s.ReserveInventory(
        inventory_pb2.ReserveRequest(
            product_id="PROD-002", quantity=10, reservation_id="R-PARTIAL"
        ),
        ctx,
    )
    assert ctx._code == grpc.StatusCode.OK, ctx._details
    assert r.success is True
    assert r.remaining_stock == 15  # 25 - 10


def test_reserve_exact_quantity_succeeds():
    """
    Reserving exactly the available stock must succeed.

    PROD-004 (Monitor) starts with stock=5.  Requesting all 5 must succeed
    and leave remaining_stock=0.
    """
    s = make_servicer()
    ctx = MockContext()
    r = s.ReserveInventory(
        inventory_pb2.ReserveRequest(
            product_id="PROD-004", quantity=5, reservation_id="R-EXACT"
        ),
        ctx,
    )
    assert ctx._code == grpc.StatusCode.OK, (
        f"Expected OK but got {ctx._code.name}: {ctx._details}"
    )
    assert r.success is True, (
        "Reservation must succeed when quantity equals available stock"
    )
    assert r.remaining_stock == 0


def test_reserve_insufficient_stock_rejected():
    """Requesting more than available stock must return RESOURCE_EXHAUSTED."""
    s = make_servicer()
    ctx = MockContext()
    r = s.ReserveInventory(
        inventory_pb2.ReserveRequest(
            product_id="PROD-001", quantity=20, reservation_id="R-OVER"
        ),
        ctx,
    )
    assert ctx._code == grpc.StatusCode.RESOURCE_EXHAUSTED, (
        f"Expected RESOURCE_EXHAUSTED but got {ctx._code.name}"
    )
    assert r.success is False


def test_reserve_zero_stock_product_rejected():
    """Reserving any quantity from a product with stock=0 must fail."""
    s = make_servicer()
    ctx = MockContext()
    r = s.ReserveInventory(
        inventory_pb2.ReserveRequest(
            product_id="PROD-005", quantity=1, reservation_id="R-EMPTY"
        ),
        ctx,
    )
    assert r.success is False


def test_reserve_decrements_stock_correctly():
    """After a successful reservation, CheckInventory must reflect updated stock."""
    s = make_servicer()
    ctx = MockContext()
    s.ReserveInventory(
        inventory_pb2.ReserveRequest(
            product_id="PROD-003", quantity=5, reservation_id="R-DEC"
        ),
        ctx,
    )
    ctx2 = MockContext()
    r = s.CheckInventory(inventory_pb2.CheckRequest(product_id="PROD-003"), ctx2)
    assert r.stock == 10, (
        f"Expected stock=10 after reserving 5 from 15, got {r.stock}"
    )


def test_reserve_unknown_product_returns_not_found():
    """Reserving an unknown product must return NOT_FOUND."""
    s = make_servicer()
    ctx = MockContext()
    s.ReserveInventory(
        inventory_pb2.ReserveRequest(
            product_id="DOES-NOT-EXIST", quantity=1, reservation_id="R-NF"
        ),
        ctx,
    )
    assert ctx._code == grpc.StatusCode.NOT_FOUND


# ===========================================================================
# ListProducts tests
# ===========================================================================

def test_list_products_returns_all_five():
    """ListProducts must return exactly 5 products without raising."""
    s = make_servicer()
    ctx = MockContext()
    r = s.ListProducts(inventory_pb2.ListRequest(), ctx)
    assert len(r.products) == 5, (
        f"Expected 5 products, got {len(r.products)}"
    )


def test_list_products_correct_stock_values():
    """ListProducts must return accurate stock for all products."""
    expected_stock = {
        "PROD-001": 10,
        "PROD-002": 25,
        "PROD-003": 15,
        "PROD-004":  5,
        "PROD-005":  0,
    }
    s = make_servicer()
    ctx = MockContext()
    r = s.ListProducts(inventory_pb2.ListRequest(), ctx)
    stock_map = {p.product_id: p.stock for p in r.products}
    for pid, want in expected_stock.items():
        assert stock_map.get(pid) == want, (
            f"{pid}: expected stock={want}, got {stock_map.get(pid)}"
        )


def test_list_products_correct_names():
    """ListProducts must return the correct product name for each product."""
    expected_names = {
        "PROD-001": "Laptop",
        "PROD-002": "Mouse",
        "PROD-003": "Keyboard",
        "PROD-004": "Monitor",
        "PROD-005": "Headphones",
    }
    s = make_servicer()
    ctx = MockContext()
    r = s.ListProducts(inventory_pb2.ListRequest(), ctx)
    name_map = {p.product_id: p.name for p in r.products}
    for pid, want in expected_names.items():
        assert name_map.get(pid) == want, (
            f"{pid}: expected name={want!r}, got {name_map.get(pid)!r}"
        )


# ===========================================================================
# Instance isolation tests
# ===========================================================================

def test_instances_have_independent_inventory():
    """
    Each InventoryServicer instance must own an independent copy of the
    inventory.  A reservation through instance A must not change the stock
    visible through instance B.
    """
    s_a = make_servicer()
    s_b = make_servicer()

    # Mutate instance A
    ctx_a = MockContext()
    s_a.ReserveInventory(
        inventory_pb2.ReserveRequest(
            product_id="PROD-001", quantity=3, reservation_id="R-ISO"
        ),
        ctx_a,
    )

    # Instance B must still show the original stock
    ctx_b = MockContext()
    r_b = s_b.CheckInventory(
        inventory_pb2.CheckRequest(product_id="PROD-001"), ctx_b
    )
    assert r_b.stock == 10, (
        f"Instance B shows stock={r_b.stock} but expected 10. "
        "Instances are sharing the same inventory dict (missing deep copy)."
    )


def test_multiple_sequential_reservations():
    """
    Sequential reservations on the same instance must correctly accumulate
    stock decrements.
    """
    s = make_servicer()

    for i in range(3):
        ctx = MockContext()
        r = s.ReserveInventory(
            inventory_pb2.ReserveRequest(
                product_id="PROD-002", quantity=5, reservation_id=f"R-SEQ-{i}"
            ),
            ctx,
        )
        assert r.success is True, f"Reservation {i} failed unexpectedly"

    # 25 - 3*5 = 10
    ctx = MockContext()
    r = s.CheckInventory(inventory_pb2.CheckRequest(product_id="PROD-002"), ctx)
    assert r.stock == 10, f"Expected stock=10, got {r.stock}"
