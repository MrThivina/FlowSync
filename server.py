from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "pos_data.db"


DEFAULT_STATE = {
    "products": [
        {"id": 1, "sku": "1001", "name": "Organic Banana Bundle", "department": "Produce", "price": 2.99, "cost": 1.35, "unit": "bunch", "stock": 28, "reorder": 12, "icon": "BN"},
        {"id": 2, "sku": "1002", "name": "Red Apple Pack", "department": "Produce", "price": 4.49, "cost": 2.1, "unit": "1 kg", "stock": 34, "reorder": 10, "icon": "AP"},
        {"id": 3, "sku": "2101", "name": "Whole Milk 1L", "department": "Dairy", "price": 1.89, "cost": 0.96, "unit": "bottle", "stock": 9, "reorder": 16, "icon": "MK"},
        {"id": 4, "sku": "2102", "name": "Greek Yogurt Cup", "department": "Dairy", "price": 1.25, "cost": 0.58, "unit": "cup", "stock": 22, "reorder": 14, "icon": "YG"},
        {"id": 5, "sku": "3201", "name": "Sourdough Loaf", "department": "Bakery", "price": 3.75, "cost": 1.7, "unit": "loaf", "stock": 17, "reorder": 8, "icon": "BR"},
        {"id": 6, "sku": "3202", "name": "Butter Croissant", "department": "Bakery", "price": 1.65, "cost": 0.72, "unit": "each", "stock": 15, "reorder": 8, "icon": "CR"},
        {"id": 7, "sku": "4401", "name": "Basmati Rice 5kg", "department": "Grocery", "price": 12.8, "cost": 8.6, "unit": "bag", "stock": 8, "reorder": 10, "icon": "RC"},
        {"id": 8, "sku": "4402", "name": "Canned Tuna", "department": "Grocery", "price": 2.4, "cost": 1.2, "unit": "can", "stock": 44, "reorder": 18, "icon": "TN"},
        {"id": 9, "sku": "5501", "name": "Laundry Detergent", "department": "Household", "price": 8.99, "cost": 5.1, "unit": "2L", "stock": 13, "reorder": 10, "icon": "LD"},
        {"id": 10, "sku": "5502", "name": "Paper Towel 6 Roll", "department": "Household", "price": 6.5, "cost": 3.8, "unit": "pack", "stock": 20, "reorder": 12, "icon": "PT"},
        {"id": 11, "sku": "6601", "name": "Chicken Breast 1kg", "department": "Meat", "price": 7.95, "cost": 4.4, "unit": "pack", "stock": 19, "reorder": 9, "icon": "CH"},
        {"id": 12, "sku": "7701", "name": "Orange Juice 1L", "department": "Beverage", "price": 3.2, "cost": 1.65, "unit": "carton", "stock": 26, "reorder": 12, "icon": "OJ"},
    ],
    "customers": [
        {"id": 1, "name": "Walk-in Customer", "phone": "", "email": "", "points": 0, "tier": "None"},
        {"id": 2, "name": "Amanda Silva", "phone": "555-0144", "email": "amanda@example.com", "points": 420, "tier": "Gold"},
        {"id": 3, "name": "Noah Perera", "phone": "555-0191", "email": "noah@example.com", "points": 160, "tier": "Silver"},
        {"id": 4, "name": "Maya Chen", "phone": "555-0178", "email": "maya@example.com", "points": 92, "tier": "Member"},
    ],
    "transactions": [
        {"id": "R-10038", "time": "2026-05-13 09:14", "customerId": 2, "payment": "Card", "status": "Paid", "items": [{"id": 2, "quantity": 2}, {"id": 8, "quantity": 4}, {"id": 10, "quantity": 1}]},
        {"id": "R-10039", "time": "2026-05-13 11:27", "customerId": 1, "payment": "Cash", "status": "Paid", "items": [{"id": 5, "quantity": 2}, {"id": 6, "quantity": 6}, {"id": 12, "quantity": 2}]},
        {"id": "R-10040", "time": "2026-05-13 13:45", "customerId": 3, "payment": "Mobile", "status": "Paid", "items": [{"id": 7, "quantity": 1}, {"id": 3, "quantity": 3}, {"id": 1, "quantity": 2}]},
    ],
    "heldSales": [],
    "cart": [[1, 2], [3, 1], [5, 1]],
    "customerId": 1,
    "payment": "Card",
    "activeView": "sales",
    "activeDepartment": "All",
    "registerOpen": True,
    "taxRate": 0.08,
    "nextReceipt": 10041,
}


def connect():
    return sqlite3.connect(DB_PATH)


def init_db():
    with connect() as db:
        db.execute(
            """
            CREATE TABLE IF NOT EXISTS app_state (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                payload TEXT NOT NULL,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        exists = db.execute("SELECT 1 FROM app_state WHERE id = 1").fetchone()
        if not exists:
            db.execute(
                "INSERT INTO app_state (id, payload) VALUES (1, ?)",
                (json.dumps(DEFAULT_STATE),),
            )


def load_state():
    with connect() as db:
        row = db.execute("SELECT payload FROM app_state WHERE id = 1").fetchone()
        if not row:
            return DEFAULT_STATE
        return json.loads(row[0])


def save_state(payload):
    with connect() as db:
        db.execute(
            """
            INSERT INTO app_state (id, payload, updated_at)
            VALUES (1, ?, CURRENT_TIMESTAMP)
            ON CONFLICT(id) DO UPDATE SET
                payload = excluded.payload,
                updated_at = CURRENT_TIMESTAMP
            """,
            (json.dumps(payload),),
        )


class PosHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, PUT, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        if self.path == "/api/state":
            self.send_json(load_state())
            return
        if self.path == "/":
            self.path = "/panel.html"
        super().do_GET()

    def do_PUT(self):
        if self.path != "/api/state":
            self.send_error(404)
            return
        try:
            payload = self.read_json()
            save_state(payload)
            self.send_json({"ok": True})
        except Exception as error:
            self.send_json({"ok": False, "error": str(error)}, status=400)

    def do_POST(self):
        if self.path != "/api/reset":
            self.send_error(404)
            return
        save_state(DEFAULT_STATE)
        self.send_json(DEFAULT_STATE)

    def read_json(self):
        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length).decode("utf-8")
        return json.loads(raw or "{}")

    def send_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


if __name__ == "__main__":
    init_db()
    server = ThreadingHTTPServer(("localhost", 8000), PosHandler)
    print("FlowSync POS backend running at http://localhost:8000")
    print(f"SQLite database: {DB_PATH}")
    server.serve_forever()
