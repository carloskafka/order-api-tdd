class InMemoryStorage:
    """Minimal process-local storage used by the order tracker."""

    def __init__(self):
        self._orders = {}

    def get_order(self, order_id):
        return self._orders.get(order_id)

    def save_order(self, order):
        self._orders[order["order_id"]] = order

    def get_all_orders(self):
        return list(self._orders.values())
