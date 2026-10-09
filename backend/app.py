from flask import Flask

from backend.in_memory_storage import InMemoryStorage
from backend.order_tracker import OrderTracker

app = Flask(__name__)
app.order_tracker = OrderTracker(InMemoryStorage())
