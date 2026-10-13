class InMemoryStorage:
    """Minimal process-local storage used by the order tracker."""

    def __init__(self):
        self._orders = {}

    def get_order(self, order_id):
        order = self._orders.get(order_id)
        return order.copy() if order is not None else None

    def save_order(self, order):
        self._orders[order["order_id"]] = order.copy()

    def get_all_orders(self):
        return [order.copy() for order in self._orders.values()]

    def clear(self):
        """Remove all stored orders, for test isolation and explicit reset."""
        self._orders.clear()
