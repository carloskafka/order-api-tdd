from flask import Flask, jsonify, request

from backend.in_memory_storage import InMemoryStorage
from backend.order_tracker import (
    DuplicateOrderError,
    InvalidOrderError,
    OrderNotFoundError,
    OrderTracker,
)


def create_app(order_tracker=None):
    application = Flask(__name__)
    application.order_tracker = (
        order_tracker
        if order_tracker is not None
        else OrderTracker(InMemoryStorage())
    )

    @application.get("/api/orders")
    def list_orders():
        status = request.args.get("status")
        try:
            orders = (
                application.order_tracker.list_all_orders()
                if status is None
                else application.order_tracker.list_orders_by_status(status)
            )
        except InvalidOrderError as error:
            return jsonify(error=str(error)), 400
        return jsonify(orders), 200

    @application.post("/api/orders")
    def add_order():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(error="Request body must be a JSON object"), 400

        required_fields = ("order_id", "item_name", "quantity", "customer_id")
        missing_fields = [field for field in required_fields if field not in payload]
        if missing_fields:
            message = f"Missing required fields: {', '.join(missing_fields)}"
            return jsonify(error=message), 400

        try:
            order = application.order_tracker.add_order(
                payload["order_id"],
                payload["item_name"],
                payload["quantity"],
                payload["customer_id"],
                status=payload.get("status", "pending"),
            )
        except DuplicateOrderError as error:
            return jsonify(error=str(error)), 409
        except InvalidOrderError as error:
            return jsonify(error=str(error)), 400
        return jsonify(order), 201

    @application.get("/api/orders/<order_id>")
    def get_order(order_id):
        try:
            order = application.order_tracker.get_order_by_id(order_id)
        except InvalidOrderError as error:
            return jsonify(error=str(error)), 400
        if order is None:
            return jsonify(error=f"Order with ID '{order_id}' not found."), 404
        return jsonify(order), 200

    @application.put("/api/orders/<order_id>")
    @application.put("/api/orders/<order_id>/status")
    def update_order_status(order_id):
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(error="Request body must be a JSON object"), 400
        if "new_status" in payload:
            new_status = payload["new_status"]
        elif "status" in payload:
            new_status = payload["status"]
        else:
            return jsonify(error="new_status is required"), 400

        try:
            order = application.order_tracker.update_order_status(
                order_id, new_status
            )
        except OrderNotFoundError as error:
            return jsonify(error=str(error)), 404
        except InvalidOrderError as error:
            return jsonify(error=str(error)), 400
        return jsonify(order), 200

    return application


app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
