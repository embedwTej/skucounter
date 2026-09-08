# SKU Counter — Frontend

React + MUI dashboard matching the Dashboard / Date Wise Report / SKU Wise Report screens.

## Setup

```powershell
cd frontend
npm install
```

Point it at your backend (defaults to `http://localhost:8000`):

```
# .env
VITE_API_BASE_URL=http://localhost:8000
```

Run it:

```powershell
npm run dev
```

Opens at `http://localhost:5173`. The Dashboard polls `/api/dashboard` every 5 seconds for live-ish updates — swap this for a websocket/SSE subscription later if you want true push updates on the UI side too (the backend already has the pattern from the device-ingestion side to copy).

## Structure

- `src/pages/Dashboard.jsx` — stat cards, SKU table, bar chart, report shortcuts
- `src/pages/DateWiseReport.jsx` — date range + shift filter, summary table, CSV export
- `src/pages/SkuWiseReport.jsx` — date range + shift + SKU filter, summary table
- `src/components/Sidebar.jsx`, `TopBar.jsx` — shared shell (nav, camera status, admin, reset button)
- `src/api.js` — all backend calls in one place

## Known gaps vs. the mockups

- SKU **Shape** icons are text for now (circle/square/triangle/hexagon) since the backend doesn't yet have shape data populated — see backend README's note on SKU metadata.
- Table pagination shown in your mockups isn't wired up yet (everything renders in one page); trivial to add once you confirm expected page size.
