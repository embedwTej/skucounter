# SKU Counter — Backend

FastAPI service that:
1. Accepts a WebSocket connection from the camera vision device at `/ws/ingest` and stores each inspected part in Postgres.
2. Serves REST endpoints for the Dashboard, Date Wise Report, and SKU Wise Report screens.

## 1. Setup (Windows / PyCharm)

```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create the Postgres database once:

```sql
CREATE DATABASE sku_counter;
```

Set the connection string (adjust user/password/host):

```powershell
$env:DATABASE_URL = "postgresql+psycopg2://postgres:postgres@localhost:5432/sku_counter"
```

Or drop a `.env` file next to `config.py`:

```
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/sku_counter
```

Run it:

```powershell
python main.py
```

Tables are created automatically on startup (`Base.metadata.create_all`). For a real production rollout you'd want Alembic migrations instead — happy to add that once the schema settles.

## 2. Test without real hardware

```powershell
python simulator.py --url ws://localhost:8000/ws/ingest --device CAM-01 --rate 2
```

This pushes fake PASS/FAIL results for 4 SKUs every 0.5s so you can see the dashboard/reports populate.

## 3. Endpoints

| Method | Path | Purpose |
|---|---|---|
| WS | `/ws/ingest` | Device pushes one JSON result per inspected part |
| GET | `/api/dashboard` | Live totals, per-SKU breakdown, camera status |
| GET | `/api/reports/date-wise?from=YYYY-MM-DD&to=YYYY-MM-DD&shift=1\|2` | Date Wise report rows |
| GET | `/api/reports/sku-wise?from=...&to=...&shift=...&sku=SKU-001` | SKU Wise report rows |
| POST | `/api/counts/reset` | Zero the live counters (body: `{"note": "shift change"}`) |

## 4. Key assumptions to double-check with you

- **Websocket payload shape** (`schemas.IncomingResult`): guessed from the `/api/results` REST response in the doc you shared (`seq`, `tsUtc`, `verdict`, `sku`, `skuId`, `qty`, `score`, `image`). If the real device sends something different (batched arrays, different field names, a "type" wrapper, etc.), send one real captured message and I'll update `schemas.py` — it's the only file that needs to change.
- **Shifts**: Shift 1 = 07:00–19:00, Shift 2 = 19:00–07:00, timezone `Asia/Kolkata` (`config.py`). Shift 2 rows are reported under the calendar date the shift *started*, matching your screenshots.
- **Images**: not stored for now (`store_images = False` in `config.py`). The image field in the payload is simply ignored on ingest. The save-to-disk path is already implemented in `ingest_service._save_image` — flip the flag to `True` whenever you want it back on, no other changes needed.
- **Reset semantics**: "Reset Count" never deletes history — it just logs a timestamp. "Current" (live, since-last-reset) and "Today" (full calendar day) counts are computed independently, matching the reset response shape in your Postman doc.
- **No auth on the websocket yet** — `ws_shared_secret` in `config.py` is there to enable a simple shared-key check (`ws://host:8000/ws/ingest?key=...`) whenever you're ready; currently blank/disabled for local testing.
- **SKU metadata** (name, shape) isn't in the payload doc, so SKUs are auto-created from `sku`/`skuId` on first sighting with `name`/`shape` left blank. You'll want a small setup step (or a one-time SQL insert) to fill in the friendly names/shapes shown in your screenshots (e.g. "70gms Onion Chicken").
