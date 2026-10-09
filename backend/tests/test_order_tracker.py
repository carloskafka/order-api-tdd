from unittest.mock import Mock

import pytest

from backend.order_tracker import OrderTracker


@pytest.fixture
def mock_storage():
    storage = Mock()
    storage.get_order.return_value = None
    storage.get_all_orders.return_value = []
    return storage


@pytest.fixture
def order_tracker(mock_storage):
    return OrderTracker(mock_storage)


def test_add_order_successfully(order_tracker, mock_storage):
    order = order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")

    assert order == {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending",
    }
    mock_storage.save_order.assert_called_once_with(order)


def test_add_order_raises_error_if_exists(order_tracker, mock_storage):
    mock_storage.get_order.return_value = {"order_id": "ORD_EXISTING"}

    with pytest.raises(
        ValueError,
        match="Order with ID 'ORD_EXISTING' already exists\\.",
    ):
        order_tracker.add_order("ORD_EXISTING", "New Item", 1, "CUST001")

    mock_storage.save_order.assert_not_called()


@pytest.mark.parametrize(
    ("order_id", "item_name", "quantity", "customer_id"),
    [
        ("", "Laptop", 1, "CUST001"),
        ("ORD001", "", 1, "CUST001"),
        ("ORD001", "Laptop", 0, "CUST001"),
        ("ORD001", "Laptop", True, "CUST001"),
        ("ORD001", "Laptop", 1, ""),
    ],
)
def test_add_order_rejects_invalid_fields(
    order_tracker, mock_storage, order_id, item_name, quantity, customer_id
):
    with pytest.raises(ValueError):
        order_tracker.add_order(order_id, item_name, quantity, customer_id)

    mock_storage.save_order.assert_not_called()


def test_add_order_accepts_an_explicit_valid_status(order_tracker, mock_storage):
    order = order_tracker.add_order(
        "ORD001", "Laptop", 1, "CUST001", status="processing"
    )

    assert order["status"] == "processing"
    mock_storage.save_order.assert_called_once_with(order)


def test_add_order_rejects_invalid_status(order_tracker, mock_storage):
    with pytest.raises(ValueError):
        order_tracker.add_order("ORD001", "Laptop", 1, "CUST001", status="lost")

    mock_storage.get_order.assert_not_called()
    mock_storage.save_order.assert_not_called()


def test_get_order_by_id_returns_existing_order(order_tracker, mock_storage):
    expected = {"order_id": "ORD001", "status": "pending"}
    mock_storage.get_order.return_value = expected

    assert order_tracker.get_order_by_id("ORD001") == expected
    mock_storage.get_order.assert_called_once_with("ORD001")


def test_get_order_by_id_returns_none_when_missing(order_tracker, mock_storage):
    mock_storage.get_order.return_value = None

    assert order_tracker.get_order_by_id("ORD404") is None


def test_get_order_by_id_rejects_empty_id(order_tracker, mock_storage):
    with pytest.raises(ValueError):
        order_tracker.get_order_by_id("")

    mock_storage.get_order.assert_not_called()


def test_update_order_status_saves_a_copy_with_new_status(
    order_tracker, mock_storage
):
    original = {
        "order_id": "ORD001",
        "item_name": "Laptop",
        "quantity": 1,
        "customer_id": "CUST001",
        "status": "pending",
    }
    mock_storage.get_order.return_value = original

    updated = order_tracker.update_order_status("ORD001", "shipped")

    assert updated["status"] == "shipped"
    assert original["status"] == "pending"
    mock_storage.save_order.assert_called_once_with(updated)
    assert updated is not original


def test_update_order_status_rejects_invalid_status_before_storage_read(
    order_tracker, mock_storage
):
    with pytest.raises(ValueError):
        order_tracker.update_order_status("ORD001", "lost")

    mock_storage.get_order.assert_not_called()


def test_update_order_status_rejects_missing_order(order_tracker, mock_storage):
    mock_storage.get_order.return_value = None

    with pytest.raises(ValueError):
        order_tracker.update_order_status("ORD404", "shipped")

    mock_storage.save_order.assert_not_called()


def test_list_all_orders_returns_storage_contents(order_tracker, mock_storage):
    orders = [{"order_id": "ORD001"}, {"order_id": "ORD002"}]
    mock_storage.get_all_orders.return_value = orders

    assert order_tracker.list_all_orders() == orders


def test_list_orders_by_status_returns_only_matching_orders(
    order_tracker, mock_storage
):
    orders = [
        {"order_id": "ORD001", "status": "pending"},
        {"order_id": "ORD002", "status": "shipped"},
    ]
    mock_storage.get_all_orders.return_value = orders

    assert order_tracker.list_orders_by_status("shipped") == [orders[1]]


@pytest.mark.parametrize("status", ["", "unknown", None])
def test_list_orders_by_status_rejects_empty_or_invalid_status(
    order_tracker, mock_storage, status
):
    with pytest.raises(ValueError):
        order_tracker.list_orders_by_status(status)

    mock_storage.get_all_orders.assert_not_called()
