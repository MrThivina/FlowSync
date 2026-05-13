# FlowSync

FlowSync is a browser-based supermarket POS system with a small Node.js backend for persistent local storage.

## Repository Contents

- `panel.html` - POS front end.
- `server.js` - Local POS backend and static file server.
- `pos_data.json` - JSON data store created automatically when the backend starts.
- `none.py` - Existing Python artifact from the original scaffold.

## Getting Started

Run the POS backend:

```powershell
node server.js
```

Then open:

```text
http://localhost:8000
```

## Usage

The POS stores products, customers, receipts, held sales, cart state, register settings, and inventory changes in `pos_data.json` through `/api/state`. If the backend is offline, the front end temporarily falls back to browser `localStorage`.

Useful API routes:

- `GET /api/state` - Load the current POS state.
- `PUT /api/state` - Save the current POS state.
- `POST /api/reset` - Reset demo data.

## License

No license has been added yet.
