# FlowSync

FlowSync is a browser-based supermarket POS system with a small Python backend for persistent local storage.

## Repository Contents

- `panel.html` - POS front end.
- `server.py` - Local POS backend and static file server.
- `pos_data.db` - SQLite database created automatically when the backend starts.
- `none.py` - Existing Python artifact from the original scaffold.

## Getting Started

Run the POS backend:

```powershell
python server.py
```

Then open:

```text
http://localhost:8000
```

## Usage

The POS stores products, customers, receipts, held sales, cart state, register settings, and inventory changes in SQLite through `/api/state`. If the backend is offline, the front end temporarily falls back to browser `localStorage`.

Useful API routes:

- `GET /api/state` - Load the current POS state.
- `PUT /api/state` - Save the current POS state.
- `POST /api/reset` - Reset demo data.

## License

No license has been added yet.
