import datetime as dt
import logging

from fastapi import Depends, FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from sqlalchemy.orm import Session

from config import settings
from database import Base, SessionLocal, engine, get_db
from ingest_service import store_incoming_result
from models import DeviceConnection
from reports import get_dashboard, get_date_wise_report, get_sku_wise_report, reset_counts
from schemas import (
    DashboardResponse,
    DateWiseResponse,
    IncomingResult,
    ResetRequest,
    ResetResponse,
    SkuWiseResponse,
)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("sku-counter")

app = FastAPI(title="SKU Counter Backend")

# Loosen this to your actual frontend origin in production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    log.info("Database tables ensured.")


@app.get("/")
def root():
    return {"status": "ok", "service": "SKU Counter API", "docs": "/docs"}


# ---------------------------------------------------------------------------
# WebSocket ingestion -- the device connects here and pushes one JSON
# message per inspected part. See schemas.IncomingResult for the expected
# shape; adjust that model if the real device payload differs.
# ---------------------------------------------------------------------------
@app.websocket(settings.ws_ingest_path)
async def ws_ingest(websocket: WebSocket):
    # Optional shared-secret check, e.g. ws://host:8000/ws/ingest?key=xxx
    if settings.ws_shared_secret:
        key = websocket.query_params.get("key")
        if key != settings.ws_shared_secret:
            await websocket.close(code=4401)
            return

    await websocket.accept()
    device_name = websocket.query_params.get("device")

    db: Session = SessionLocal()
    db.add(DeviceConnection(device=device_name, connected=True, ts_utc=dt.datetime.now(dt.timezone.utc)))
    db.commit()
    log.info("Device connected: %s", device_name)

    try:
        while True:
            raw = await websocket.receive_json()
            try:
                payload = IncomingResult.model_validate(raw)
            except ValidationError as e:
                log.warning("Bad payload from %s: %s", device_name, e)
                await websocket.send_json({"ok": False, "error": "validation_error", "detail": str(e)})
                continue

            event = store_incoming_result(db, payload)
            await websocket.send_json({"ok": True, "seq": event.device_seq})

    except WebSocketDisconnect:
        log.info("Device disconnected: %s", device_name)
    finally:
        db.add(DeviceConnection(device=device_name, connected=False, ts_utc=dt.datetime.now(dt.timezone.utc)))
        db.commit()
        db.close()


# ---------------------------------------------------------------------------
# REST API for the dashboard / report UI
# ---------------------------------------------------------------------------
@app.get("/api/dashboard", response_model=DashboardResponse)
def api_dashboard(db: Session = Depends(get_db)):
    return get_dashboard(db)


@app.get("/api/reports/date-wise", response_model=DateWiseResponse)
def api_date_wise(
    from_date: dt.date = Query(..., alias="from"),
    to_date: dt.date = Query(..., alias="to"),
    shift: int | None = Query(None, ge=1, le=2),
    db: Session = Depends(get_db),
):
    if from_date > to_date:
        raise HTTPException(400, "from date must be before to date")
    return get_date_wise_report(db, from_date, to_date, shift)


@app.get("/api/reports/sku-wise", response_model=SkuWiseResponse)
def api_sku_wise(
    from_date: dt.date = Query(..., alias="from"),
    to_date: dt.date = Query(..., alias="to"),
    shift: int | None = Query(None, ge=1, le=2),
    sku: str | None = Query(None),
    db: Session = Depends(get_db),
):
    if from_date > to_date:
        raise HTTPException(400, "from date must be before to date")
    return get_sku_wise_report(db, from_date, to_date, shift, sku)


@app.post("/api/counts/reset", response_model=ResetResponse)
def api_reset(body: ResetRequest = ResetRequest(), db: Session = Depends(get_db)):
    counts = reset_counts(db, body.note)
    return ResetResponse(reset=True, ts_utc=dt.datetime.now(dt.timezone.utc), counts=counts)


if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.environ.get("PORT", settings.port))
    uvicorn.run("main:app", host=settings.host, port=port)
