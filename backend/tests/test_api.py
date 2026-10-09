import pytest

from backend.app import app
from backend.in_memory_storage import InMemoryStorage
from backend.order_tracker import OrderTracker


@pytest.fixture
def client():
    app.config.update(TESTING=True)
    app.order_tracker = OrderTracker(InMemoryStorage())
    return app.test_client()


@pytest.fixture
def order_payload():
    return {
        "order_id": "ORD001",
        "item_name": "Headphones",
        "quantity": 1,
        "customer_id": "CUST001",
    }


def test_add_order_api_success(client, order_payload):
    response = client.post("/api/orders", json=order_payload)

    assert response.status_code == 201
    assert response.get_json() == {**order_payload, "status": "pending"}


def test_add_order_api_rejects_duplicate_id(client, order_payload):
    client.post("/api/orders", json=order_payload)

    response = client.post("/api/orders", json=order_payload)

    assert response.status_code == 409
    assert "error" in response.get_json()


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {
            "order_id": "ORD001",
            "item_name": "",
            "quantity": 1,
            "customer_id": "CUST001",
        },
        {
            "order_id": "ORD001",
            "item_name": "Laptop",
            "quantity": 0,
            "customer_id": "CUST001",
        },
    ],
)
def test_add_order_api_rejects_invalid_data(client, payload):
    response = client.post("/api/orders", json=payload)

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_get_order_api_returns_order(client, order_payload):
    client.post("/api/orders", json=order_payload)

    response = client.get("/api/orders/ORD001")

    assert response.status_code == 200
    assert response.get_json() == {**order_payload, "status": "pending"}


def test_get_order_api_returns_404_for_missing_order(client):
    response = client.get("/api/orders/MISSING")

    assert response.status_code == 404


def test_update_order_api_accepts_documented_put_contract(
    client, order_payload
):
    client.post("/api/orders", json=order_payload)

    response = client.put(
        "/api/orders/ORD001",
        json={"new_status": "shipped"},
    )

    assert response.status_code == 200
    assert response.get_json() == {**order_payload, "status": "shipped"}


def test_update_order_api_accepts_status_path_contract(client, order_payload):
    client.post("/api/orders", json=order_payload)

    response = client.put(
        "/api/orders/ORD001/status",
        json={"status": "delivered"},
    )

    assert response.status_code == 200
    assert response.get_json()["status"] == "delivered"


def test_update_order_api_returns_404_for_missing_order(client):
    response = client.put(
        "/api/orders/MISSING",
        json={"new_status": "shipped"},
    )

    assert response.status_code == 404


def test_update_order_api_rejects_invalid_status(client, order_payload):
    client.post("/api/orders", json=order_payload)

    response = client.put(
        "/api/orders/ORD001",
        json={"new_status": "lost"},
    )

    assert response.status_code == 400


def test_list_orders_api_returns_all_and_filters_by_status(
    client, order_payload
):
    client.post("/api/orders", json=order_payload)
    client.post(
        "/api/orders",
        json={**order_payload, "order_id": "ORD002", "status": "shipped"},
    )

    all_orders = client.get("/api/orders")
    shipped_orders = client.get("/api/orders?status=shipped")

    assert all_orders.status_code == 200
    assert len(all_orders.get_json()) == 2
    assert [order["order_id"] for order in shipped_orders.get_json()] == [
        "ORD002"
    ]


def test_list_orders_api_rejects_invalid_filter(client):
    response = client.get("/api/orders?status=")

    assert response.status_code == 400
