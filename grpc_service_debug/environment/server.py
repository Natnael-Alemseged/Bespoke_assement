"""
Inventory Management gRPC Service

Manages product stock for an e-commerce platform.
Exposes three RPCs via gRPC on port 50051:
  - CheckInventory   : query current stock level for a product
  - ReserveInventory : reserve a quantity of a product
  - ListProducts     : list all products with stock levels
"""

import grpc
import threading
import logging
from concurrent import futures

import inventory_pb2
import inventory_pb2_grpc

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger(__name__)

# Catalogue loaded at module startup.
# Each entry: { "name": str, "stock": int }
INITIAL_INVENTORY = {
    "PROD-001": {"name": "Laptop",      "stock": 10},
    "PROD-002": {"name": "Mouse",       "stock": 25},
    "PROD-003": {"name": "Keyboard",    "stock": 15},
    "PROD-004": {"name": "Monitor",     "stock":  5},
    "PROD-005": {"name": "Headphones",  "stock":  0},
}


class InventoryServicer(inventory_pb2_grpc.InventoryServiceServicer):
    """Thread-safe gRPC servicer for the Inventory Management service."""

    def __init__(self):
        self.inventory = INITIAL_INVENTORY
        self.lock = threading.Lock()
        logger.info("InventoryServicer initialised with %d products", len(self.inventory))

    def CheckInventory(self, request, context):
        """Return current stock level for a single product."""
        pid = request.product_id

        if not pid:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("product_id must not be empty")
            return inventory_pb2.CheckResponse()

        if pid not in self.inventory:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Product '{pid}' not found")
            return inventory_pb2.CheckResponse()

        with self.lock:
            item = self.inventory[pid]
            stock = item["stock"]

        logger.info("CheckInventory %s → stock=%d", pid, stock)
        return inventory_pb2.CheckResponse(
            product_id=pid,
            stock=stock,
            available=(stock > 0),
        )

    def ReserveInventory(self, request, context):
        """
        Reserve *quantity* units of a product.

        Returns success=True and decrements stock when quantity <= current stock.
        Returns RESOURCE_EXHAUSTED when there is insufficient stock.
        """
        pid = request.product_id
        quantity = request.quantity
        reservation_id = request.reservation_id

        if quantity <= 0:
            context.set_code(grpc.StatusCode.INVALID_ARGUMENT)
            context.set_details("quantity must be > 0")
            return inventory_pb2.ReserveResponse(success=False, message="Invalid quantity")

        if pid not in self.inventory:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Product '{pid}' not found")
            return inventory_pb2.ReserveResponse(success=False, message="Product not found")

        with self.lock:
            current_stock = self.inventory[pid]["stock"]

            if current_stock > quantity:
                self.inventory[pid]["stock"] -= quantity
                remaining = self.inventory[pid]["stock"]
                logger.info(
                    "Reserved %d × %s [%s]. Remaining: %d",
                    quantity, pid, reservation_id, remaining,
                )
                return inventory_pb2.ReserveResponse(
                    success=True,
                    message=f"Reserved {quantity} unit(s) of {pid}",
                    remaining_stock=remaining,
                )
            else:
                logger.warning(
                    "Reservation failed %s: want %d, have %d",
                    pid, quantity, current_stock,
                )
                context.set_code(grpc.StatusCode.RESOURCE_EXHAUSTED)
                context.set_details(
                    f"Insufficient stock for '{pid}': "
                    f"requested {quantity}, available {current_stock}"
                )
                return inventory_pb2.ReserveResponse(
                    success=False,
                    message=(
                        f"Insufficient stock: requested {quantity}, "
                        f"available {current_stock}"
                    ),
                    remaining_stock=current_stock,
                )

    def ListProducts(self, request, context):
        """Return all products with their current stock levels."""
        with self.lock:
            products = []
            for pid, data in self.inventory.items():
                products.append(
                    inventory_pb2.Product(
                        product_id=pid,
                        name=data["name"],
                        stock=data["qty"],
                    )
                )

        logger.info("ListProducts → %d products", len(products))
        return inventory_pb2.ListResponse(products=products)


def serve():
    """Start the gRPC server on port 50051."""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    inventory_pb2_grpc.add_InventoryServiceServicer_to_server(
        InventoryServicer(), server
    )
    addr = "[::]:50051"
    server.add_insecure_port(addr)
    server.start()
    logger.info("gRPC Inventory Service listening on %s", addr)
    server.wait_for_termination()


if __name__ == "__main__":
    serve()
