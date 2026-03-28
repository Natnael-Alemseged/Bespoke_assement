"""
Functional end-to-end tests for the Inventory Management gRPC Service.

Each test that talks to the running service gets a **fresh** server process with
pristine inventory (function-scoped `stub` fixture). Reservation and check tests
therefore do not depend on execution order or shared mutable state.

grpcio and protobuf are pre-installed in the Docker image (requirements.txt).
We add the system site-packages directory to sys.path so the uvx-managed
test Python can import them without a separate install step.
"""

import subprocess
import sys
import time

# ── Dependency path setup ────────────────────────────────────────────────────
_SITE = "/usr/local/lib/python3.12/site-packages"
if _SITE not in sys.path:
    sys.path.insert(0, _SITE)

sys.path.insert(0, "/app")

import grpc                            # noqa: E402
import pytest                          # noqa: E402
import inventory_pb2                   # noqa: E402
import inventory_pb2_grpc              # noqa: E402

_ADDR = "localhost:50051"


def _stop_server(proc, channel):
    """Terminate gRPC server and release the client channel."""
    try:
        channel.close()
    except Exception:
        pass
    if proc is None or proc.poll() is not None:
        return
    proc.terminate()
    try:
        proc.wait(timeout=5)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
    # Brief pause so the next bind to 50051 succeeds reliably across platforms.
    time.sleep(0.25)


def _start_server():
    """Spawn `/app/server.py`, wait until the port accepts connections, return stub."""
    proc = subprocess.Popen(
        ["/usr/local/bin/python3", "/app/server.py"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    channel = grpc.insecure_channel(_ADDR)
    try:
        grpc.channel_ready_future(channel).result(timeout=30)
    except grpc.FutureTimeoutError:
        _stop_server(proc, channel)
        raise RuntimeError(
            "gRPC server did not become ready within 30 s — "
            "ensure /app/server.py starts without errors."
        )
    stub = inventory_pb2_grpc.InventoryServiceStub(channel)
    return proc, channel, stub


@pytest.fixture
def stub():
    """Fresh Inventory gRPC server and client for each test (isolated inventory)."""
    proc, channel, st = _start_server()
    yield st
    _stop_server(proc, channel)

# ===========================================================================
# CheckInventory — functional E2E tests
# ===========================================================================

def test_check_inventory_laptop(stub):
    """PROD-001 (Laptop) must report stock=10 and available=True."""
    r = stub.CheckInventory(inventory_pb2.CheckRequest(product_id="PROD-001"))
    assert r.product_id == "PROD-001"
    assert r.stock == 10
    assert r.available is True


def test_check_inventory_out_of_stock(stub):
    """PROD-005 (Headphones, stock=0) must be marked available=False."""
    r = stub.CheckInventory(inventory_pb2.CheckRequest(product_id="PROD-005"))
    assert r.stock == 0
    assert r.available is False


def test_check_inventory_not_found(stub):
    """Unknown product IDs must raise a NOT_FOUND RPC error."""
    with pytest.raises(grpc.RpcError) as exc:
        stub.CheckInventory(inventory_pb2.CheckRequest(product_id="UNKNOWN-999"))
    assert exc.value.code() == grpc.StatusCode.NOT_FOUND


def test_check_inventory_all_initial_values(stub):
    """All five products must report their correct initial stock."""
    expected = {"PROD-001": 10, "PROD-002": 25, "PROD-003": 15,
                "PROD-004": 5,  "PROD-005": 0}
    for pid, want in expected.items():
        r = stub.CheckInventory(inventory_pb2.CheckRequest(product_id=pid))
        assert r.stock == want, f"{pid}: expected {want}, got {r.stock}"


# ===========================================================================
# ListProducts — validates Bug 2 fix (data["qty"] → data["stock"])
# ===========================================================================

def test_list_products_count(stub):
    """ListProducts must return all 5 products without raising."""
    r = stub.ListProducts(inventory_pb2.ListRequest())
    assert len(r.products) == 5


def test_list_products_stock_values(stub):
    """ListProducts must return the correct initial stock for every product."""
    expected = {"PROD-001": 10, "PROD-002": 25, "PROD-003": 15,
                "PROD-004": 5,  "PROD-005": 0}
    r = stub.ListProducts(inventory_pb2.ListRequest())
    stock_map = {p.product_id: p.stock for p in r.products}
    for pid, want in expected.items():
        assert stock_map.get(pid) == want, (
            f"{pid}: expected stock={want}, got {stock_map.get(pid)}"
        )


def test_list_products_names(stub):
    """ListProducts must return the correct name for each product."""
    expected = {"PROD-001": "Laptop", "PROD-002": "Mouse",
                "PROD-003": "Keyboard", "PROD-004": "Monitor",
                "PROD-005": "Headphones"}
    r = stub.ListProducts(inventory_pb2.ListRequest())
    name_map = {p.product_id: p.name for p in r.products}
    for pid, want in expected.items():
        assert name_map.get(pid) == want, (
            f"{pid}: expected {want!r}, got {name_map.get(pid)!r}"
        )


# ===========================================================================
# ReserveInventory — mutations (isolated server per test)
# ===========================================================================

def test_reserve_partial_quantity_succeeds(stub):
    """Reserving fewer units than available must succeed.
    PROD-002 (Mouse, 25): reserve 5 → remaining=20.
    """
    r = stub.ReserveInventory(
        inventory_pb2.ReserveRequest(
            product_id="PROD-002", quantity=5, reservation_id="R-PARTIAL"
        )
    )
    assert r.success is True
    assert r.remaining_stock == 20


def test_reserve_exact_quantity_succeeds(stub):
    """Reserving exactly the available stock must succeed.
    PROD-004 (Monitor, stock=5): reserve 5 → remaining=0.
    Validates Bug 1 fix: the condition must be >= not >.
    """
    r = stub.ReserveInventory(
        inventory_pb2.ReserveRequest(
            product_id="PROD-004", quantity=5, reservation_id="R-EXACT"
        )
    )
    assert r.success is True, (
        "Reservation must succeed when quantity == available stock. "
        f"Response: {r}"
    )
    assert r.remaining_stock == 0


def test_reserve_over_stock_raises_resource_exhausted(stub):
    """Requesting more than available stock must raise RESOURCE_EXHAUSTED.
    PROD-001 (Laptop, stock=10): try to reserve 20.
    """
    with pytest.raises(grpc.RpcError) as exc:
        stub.ReserveInventory(
            inventory_pb2.ReserveRequest(
                product_id="PROD-001", quantity=20, reservation_id="R-OVER"
            )
        )
    assert exc.value.code() == grpc.StatusCode.RESOURCE_EXHAUSTED


def test_reserve_zero_stock_raises_resource_exhausted(stub):
    """Reserving from a product with stock=0 must raise RESOURCE_EXHAUSTED.
    PROD-005 (Headphones, stock=0): try to reserve 1.
    """
    with pytest.raises(grpc.RpcError) as exc:
        stub.ReserveInventory(
            inventory_pb2.ReserveRequest(
                product_id="PROD-005", quantity=1, reservation_id="R-EMPTY"
            )
        )
    assert exc.value.code() == grpc.StatusCode.RESOURCE_EXHAUSTED


def test_reserve_decrements_stock_correctly(stub):
    """A successful reservation must decrease the stock returned by CheckInventory.
    PROD-003 (Keyboard, 15): reserve 6 → expect stock=9 on next check.
    """
    stub.ReserveInventory(
        inventory_pb2.ReserveRequest(
            product_id="PROD-003", quantity=6, reservation_id="R-DECREMENT"
        )
    )
    r = stub.CheckInventory(inventory_pb2.CheckRequest(product_id="PROD-003"))
    assert r.stock == 9, f"Expected 9 after reserving 6 from 15, got {r.stock}"


def test_sequential_reservations_accumulate_correctly(stub):
    """Three sequential reservations must each decrement stock correctly.
    PROD-001 (Laptop, stock=10): reserve 3 three times → final stock=1.
    """
    for i in range(3):
        r = stub.ReserveInventory(
            inventory_pb2.ReserveRequest(
                product_id="PROD-001", quantity=3, reservation_id=f"SEQ-{i}"
            )
        )
        assert r.success is True, f"Sequential reservation {i} failed: {r}"

    r = stub.CheckInventory(inventory_pb2.CheckRequest(product_id="PROD-001"))
    assert r.stock == 1, f"Expected stock=1 after 3×3 reservations from 10, got {r.stock}"


# ===========================================================================
# Instance isolation — unit test (validates Bug 3 fix)
# Two separate InventoryServicer instances must have independent inventory.
# ===========================================================================

from server import InventoryServicer as _Servicer  # noqa: E402


class _MockCtx:
    def __init__(self):
        self._code = grpc.StatusCode.OK
        self._details = ""

    def set_code(self, c):
        self._code = c

    def set_details(self, d):
        self._details = d


def test_instances_have_independent_inventory():
    """Each InventoryServicer instance must own its own copy of the inventory.
    A mutation via instance A must not be visible through instance B.
    """
    a = _Servicer()
    b = _Servicer()

    a.ReserveInventory(
        inventory_pb2.ReserveRequest(
            product_id="PROD-001", quantity=3, reservation_id="ISO"
        ),
        _MockCtx(),
    )

    ctx = _MockCtx()
    r = b.CheckInventory(
        inventory_pb2.CheckRequest(product_id="PROD-001"), ctx
    )
    assert r.stock == 10, (
        f"Instance B shows stock={r.stock}, expected 10. "
        "Instances are sharing the same inventory dict (missing deep copy)."
    )
