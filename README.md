# Order Tracking Service

A minimal Flask order-tracking API built with a test-first Red → Green →
Refactor workflow. Business rules are in `backend/order_tracker.py`; the
framework-agnostic storage adapter is in `backend/in_memory_storage.py`; Flask
routes are in `backend/app.py`.

## Setup and run

Python 3.13 is preferred to match the Udacity Workspace.

```bash
python3 -m venv venv
source venv/bin/activate
python -m pip install -r backend/requirements.txt
pytest
python -m backend.app
```

Run pytest from the repository root. `pytest.ini` configures test discovery and
the import path. The Flask server listens on `0.0.0.0:5000`; open
`http://127.0.0.1:5000` locally or use the Workspace's Flask App link. Orders
are stored in memory and disappear when the server process restarts.

## TDD workflow

The commit history records the cycle: the `test: ... (red)` commit adds the
behavior tests and produces failing tests against the skeleton; the `feat: ...
(green)` commit implements the behavior and makes the suite pass; the
`refactor: ... (refactor)` commit simplifies error responses without changing
behavior. Tests are split between mock-storage unit tests in
`backend/tests/test_order_tracker.py` and Flask test-client integration tests
in `backend/tests/test_api.py`.

The original completed implementation was used as a behavioral reference while
reconstructing this repository's staged history; the Red commit contains the
tests before the functional backend implementation. The suite records 31
expected failures at Red and 33 passing tests at Green and after Refactor.

## Order model and API

Each order has this shape:

```json
{
  "order_id": "ORD001",
  "item_name": "Headphones",
  "quantity": 1,
  "customer_id": "CUST001",
  "status": "pending"
}
```

Required strings must be non-empty; quantity must be a positive integer
(booleans are rejected). Status defaults to `pending` and must be one of
`pending`, `processing`, `shipped`, `delivered`, or `cancelled`.

| Method | Path | Behavior |
| --- | --- | --- |
| `POST` | `/api/orders` | Create an order; returns `201` |
| `GET` | `/api/orders/<order_id>` | Fetch an order; returns `200` or `404` |
| `PUT` | `/api/orders/<order_id>` | Update with `{"new_status":"shipped"}` |
| `PUT` | `/api/orders/<order_id>/status` | Compatible variant accepting `status` or `new_status` |
| `GET` | `/api/orders` | List all orders |
| `GET` | `/api/orders?status=shipped` | Filter by status |

Invalid input returns `400`, duplicate IDs return `409`, and missing orders
return `404`. Error responses are JSON objects containing an `error` field.

## Reflection

I kept order rules separate from Flask and injected storage, which makes the
business logic independently testable while keeping the first version
lightweight. The Red-stage failures helped identify the missing behavior before
implementation; mock-storage tests also verify that status updates save a copy
instead of mutating stored records. The in-memory adapter is intentionally
simple, so its tradeoff is losing orders on restart. The focused unit and API
test files make failures easier to locate and new cases easier to add. I feel
motivated to continue practicing test-first development. If I extended the
project, I would add durable storage and test it with the same storage contract.
