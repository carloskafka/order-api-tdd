class DuplicateOrderError(ValueError):
    """Raised when an order ID is already in use."""


class OrderNotFoundError(ValueError):
    """Raised when an order cannot be found."""


class InvalidOrderError(ValueError):
    """Raised when an order contains invalid data."""


class OrderTracker:
    """Apply order rules while delegating persistence to a storage object."""

    ALLOWED_STATUSES = frozenset(
        {"pending", "processing", "shipped", "delivered", "cancelled"}
    )

    def __init__(self, storage):
        self.storage = storage

    def add_order(
        self,
        order_id,
        item_name,
        quantity,
        customer_id,
        status="pending",
    ):
        order_id = self._required_text(order_id, "order_id")
        item_name = self._required_text(item_name, "item_name")
        customer_id = self._required_text(customer_id, "customer_id")
        if isinstance(quantity, bool) or not isinstance(quantity, int) or quantity <= 0:
            raise InvalidOrderError("quantity must be a positive integer")
        self._validate_status(status)

        if self.storage.get_order(order_id) is not None:
            raise DuplicateOrderError(
                f"Order with ID '{order_id}' already exists."
            )

        order = {
            "order_id": order_id,
            "item_name": item_name,
            "quantity": quantity,
            "customer_id": customer_id,
            "status": status,
        }
        self.storage.save_order(order)
        return order.copy()

    def get_order_by_id(self, order_id):
        order_id = self._required_text(order_id, "order_id")
        order = self.storage.get_order(order_id)
        return order.copy() if order is not None else None

    def update_order_status(self, order_id, new_status):
        order_id = self._required_text(order_id, "order_id")
        self._validate_status(new_status)
        order = self.storage.get_order(order_id)
        if order is None:
            raise OrderNotFoundError(f"Order with ID '{order_id}' not found.")

        updated_order = order.copy()
        updated_order["status"] = new_status
        self.storage.save_order(updated_order)
        return updated_order.copy()

    def list_all_orders(self):
        return [order.copy() for order in self.storage.get_all_orders()]

    def list_orders_by_status(self, status):
        self._validate_status(status)
        return [
            order
            for order in self.list_all_orders()
            if order.get("status") == status
        ]

    @classmethod
    def _validate_status(cls, status):
        if not isinstance(status, str) or status not in cls.ALLOWED_STATUSES:
            allowed = ", ".join(sorted(cls.ALLOWED_STATUSES))
            raise InvalidOrderError(f"status must be one of: {allowed}")

    @staticmethod
    def _required_text(value, field_name):
        if not isinstance(value, str) or not value.strip():
            raise InvalidOrderError(f"{field_name} must be a non-empty string")
        return value.strip()
