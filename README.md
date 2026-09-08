# SKU Counter — WebSocket Ingestion + Dashboard/Reports

```
sku-counter/
├── backend/     FastAPI: WebSocket ingestion -> Postgres, + REST API
└── frontend/    React + MUI: Dashboard, Date Wise Report, SKU Wise Report
```

## Quick start

1. **Backend** — see `backend/README.md`. TL;DR:
   ```powershell
   cd backend
   python -m venv venv && venv\Scripts\activate
   pip install -r requirements.txt
   $env:DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/sku_counter"
   python main.py
   ```
2. **Simulate the device** (no hardware needed to test):
   ```powershell
   python simulator.py --rate 2
   ```
3. **Frontend** — see `frontend/README.md`. TL;DR:
   ```powershell
   cd frontend
   npm install
   npm run dev
   ```
4. Open `http://localhost:5173` — you should see live counts building up on the Dashboard.

## What still needs your input

This was built from the REST-oriented Postman doc you shared plus the two screenshots, since I don't have a captured example of the actual websocket push message. Everything's centralized so corrections are cheap:

1. **Send me one real captured websocket message** from the device — I'll reconcile `backend/schemas.py` (`IncomingResult`) against it. If it batches multiple results per message, or wraps them in an envelope (`{"type": "result", "data": {...}}`), that's a small, contained change.
2. **Image storage is off for now** (per your instruction) — the field is accepted but discarded. Flip `store_images = True` in `backend/config.py` whenever you want it.
3. **SKU master data** — names ("70gms Onion Chicken") and shapes (circle/square/triangle/hexagon) aren't in the payload doc. Right now SKUs auto-create from `sku`/`skuId` with blank name/shape on first sighting. Either send me the full SKU list to seed, or I can add a small admin endpoint to edit them.
4. **Shift boundaries** — confirmed 07:00/19:00 in `Asia/Kolkata`? That's what's coded.
5. **Auth** — nothing's enforced on the websocket yet. `ws_shared_secret` in `backend/config.py` is ready to switch on when you want it.
