class OrderTracker:
    """Order business rules; implemented in the Green stage."""

    def __init__(self, storage):
        self.storage = storage

    def add_order(self, order_id, item_name, quantity, customer_id, status="pending"):
        raise NotImplementedError

    def get_order_by_id(self, order_id):
        raise NotImplementedError

    def update_order_status(self, order_id, new_status):
        raise NotImplementedError

    def list_all_orders(self):
        raise NotImplementedError

    def list_orders_by_status(self, status):
        raise NotImplementedError
