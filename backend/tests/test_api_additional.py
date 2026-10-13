import pytest

from backend.app import create_app
from backend.in_memory_storage import InMemoryStorage
from backend.order_tracker import OrderTracker


@pytest.fixture
def client():
    test_app = create_app(OrderTracker(InMemoryStorage()))
    test_app.config.update(TESTING=True)
    return test_app.test_client()


@pytest.fixture
def order_payload():
    return {
        "order_id": "ORD001",
        "item_name": "Headphones",
        "quantity": 1,
        "customer_id": "CUST001",
    }


def test_create_order_rejects_duplicate_id(client, order_payload):
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
def test_create_order_rejects_invalid_data(client, payload):
    response = client.post("/api/orders", json=payload)

    assert response.status_code == 400
    assert "error" in response.get_json()


def test_update_order_api_accepts_documented_put_contract(client, order_payload):
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


def test_list_orders_api_rejects_invalid_filter(client):
    response = client.get("/api/orders?status=")

    assert response.status_code == 400


def test_list_orders_api_returns_empty_list_before_any_order(client):
    response = client.get("/api/orders")

    assert response.status_code == 200
    assert response.get_json() == []


def test_list_orders_by_status_returns_empty_for_valid_status_without_matches(
    client, order_payload
):
    client.post("/api/orders", json=order_payload)

    response = client.get("/api/orders?status=shipped")

    assert response.status_code == 200
    assert response.get_json() == []
