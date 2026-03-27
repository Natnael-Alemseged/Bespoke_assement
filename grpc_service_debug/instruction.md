# Fix the Broken Inventory Management gRPC Service

You are working with a Python gRPC inventory management microservice located in `/app/`. The service was recently refactored and is now failing. Your goal is to identify **all bugs** in the server implementation and fix them so the service works correctly.

## Service Overview

The service manages product stock for an e-commerce platform and exposes three gRPC operations:

- **`CheckInventory`** – Returns the current stock level and availability status for a given product.
- **`ReserveInventory`** – Attempts to reserve a specified quantity of a product. Succeeds when there is sufficient stock; returns a `RESOURCE_EXHAUSTED` status when stock is insufficient.
- **`ListProducts`** – Returns all products with their names and current stock levels.

## Initial Inventory

The service is pre-loaded with the following products:

| Product ID | Name        | Stock |
|------------|-------------|-------|
| PROD-001   | Laptop      | 10    |
| PROD-002   | Mouse       | 25    |
| PROD-003   | Keyboard    | 15    |
| PROD-004   | Monitor     | 5     |
| PROD-005   | Headphones  | 0     |

## Requirements

Your fix must ensure that all of the following are true:

1. **`CheckInventory`** returns the correct `stock` count and sets `available=True` only when `stock > 0` for every product in the table above.

2. **`ReserveInventory`** succeeds (returns `success=True`) when the requested quantity is **less than or equal to** the available stock. After a successful reservation, `remaining_stock` must reflect the decremented value.

3. **`ReserveInventory`** returns `success=False` with a `RESOURCE_EXHAUSTED` gRPC status code when the requested quantity exceeds available stock.

4. **`ListProducts`** returns all 5 products with their correct names and stock values without raising any errors.

5. The service implementation must correctly manage **independent inventory state per instance**. Each instantiation of the service class must begin with a fresh copy of the initial inventory; operations through one instance must not affect another instance's inventory.

## Files

- `/app/server.py` — The main gRPC server implementation. **This is the only file that contains bugs.**
- `/app/inventory.proto` — The protobuf service definition (for reference only).
- `/app/inventory_pb2.py` — Generated protobuf message classes (do not modify).
- `/app/inventory_pb2_grpc.py` — Generated gRPC service stubs (do not modify).
- `/app/requirements.txt` — Python dependencies.

## Running the Server

```bash
cd /app && python server.py
```

## Hints

- Start by running the server and exercising each RPC to observe failure modes.
- Read error output carefully — tracebacks will point you toward the issues.
- There are **exactly 3 bugs**, all in `/app/server.py`.
