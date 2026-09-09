import datetime as dt
import logging

from fastapi import Depends, FastAPI, HTTPException, Query, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError
from sqlalchemy import func
from sqlalchemy.orm import Session

from config import settings
from database import Base, SessionLocal, engine, get_db
from ingest_service import store_incoming_result
from models import DeviceConnection, InspectionEvent, ResetLog, Sku
from reports import get_dashboard, get_date_wise_report, get_sku_wise_report, reset_counts
from schemas import (
    DashboardResponse,
    DateWiseResponse,
    EventsMessage,
    HelloMessage,
    ImagesMessage,
    IncomingResult,
    ResetsMessage,
    SkuMessage,
    StatusMessage,
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
    # When configured, the protocol requires a bearer token at handshake time.
    if settings.ws_shared_secret:
        authorization = websocket.headers.get("authorization")
        protocol = websocket.headers.get("x-protocol")
        if authorization != f"Bearer {settings.ws_shared_secret}" or protocol != "partcount-cloud/1":
            await websocket.close(code=4401)
            return

    await websocket.accept()
    station_id = websocket.headers.get("x-station-id") or websocket.query_params.get("device")

    db: Session = SessionLocal()
    db.add(DeviceConnection(device=station_id, connected=True, ts_utc=dt.datetime.now(dt.timezone.utc)))
    db.commit()
    log.info("Station connected: %s", station_id)
    hello_received = False

    try:
        while True:
            raw = await websocket.receive_json()
            message_type = raw.get("type")

            if message_type == "hello":
                hello = HelloMessage.model_validate(raw)
                station_id = hello.station.id
                hello_received = True
                have_event_id = (
                    db.query(func.max(InspectionEvent.device_seq))
                    .filter(InspectionEvent.device == station_id)
                    .scalar()
                    or 0
                )
                have_reset_id = db.query(func.max(ResetLog.id)).scalar() or 0
                await websocket.send_json({
                    "type": "welcome",
                    "haveEventId": have_event_id,
                    "haveImageSeq": 0,
                    "haveResetId": have_reset_id,
                    "sendImages": settings.store_images,
                    "statusIntervalS": 5,
                })
            elif not hello_received:
                await websocket.close(code=4400, reason="hello_required")
                return
            elif message_type == "skus":
                message = SkuMessage.model_validate(raw)
                for item in message.skus:
                    sku = db.query(Sku).filter(Sku.device_sku_id == item.id).one_or_none()
                    if sku is None:
                        db.add(Sku(device_sku_id=item.id, code=item.name, name=item.name))
                    else:
                        sku.name = item.name
                db.commit()
            elif message_type == "events":
                message = EventsMessage.model_validate(raw)
                for item in message.events:
                    payload = IncomingResult(
                        device=station_id,
                        seq=item.id,
                        tsUtc=item.ts,
                        verdict="PASS",
                        sku=item.sku,
                        skuId=item.skuId,
                        qty=item.qty,
                        score=item.score,
                    )
                    store_incoming_result(db, payload)
                await websocket.send_json({"type": "ack", "eventId": message.cursor})
            elif message_type == "resets":
                message = ResetsMessage.model_validate(raw)
                for item in message.resets:
                    existing = db.query(ResetLog).filter(ResetLog.id == item.id).one_or_none()
                    if existing is None:
                        db.add(ResetLog(id=item.id, ts_utc=item.ts, note=item.note, source=item.source))
                db.commit()
                await websocket.send_json({"type": "ack", "resetId": message.cursor})
            elif message_type == "images":
                message = ImagesMessage.model_validate(raw)
                await websocket.send_json({"type": "ack", "imageSeq": message.cursor})
            elif message_type == "status":
                StatusMessage.model_validate(raw)
            else:
                log.info("Ignoring unknown message type from %s: %s", station_id, message_type)

    except WebSocketDisconnect:
        log.info("Device disconnected: %s", station_id)
    finally:
        db.add(DeviceConnection(device=station_id, connected=False, ts_utc=dt.datetime.now(dt.timezone.utc)))
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
