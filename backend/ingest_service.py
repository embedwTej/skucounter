import base64
import datetime as dt
import json
import os
import uuid

from sqlalchemy.orm import Session

from config import settings
from models import InspectionEvent, Sku
from schemas import IncomingResult
from shift_utils import compute_shift


def _save_image(payload: IncomingResult) -> str | None:
    """Writes the base64 image to disk under images/<date>/<uuid>.<ext>
    and returns the path *relative to image_storage_root* to store in the DB.
    Returns None if there's no image or image storage is disabled.
    """
    if not settings.store_images or not payload.image or not payload.image.base64:
        return None

    ext = "png" if payload.image.mime == "image/png" else "jpg"
    day_folder = payload.tsUtc.strftime("%Y-%m-%d")
    folder = os.path.join(settings.image_storage_root, day_folder)
    os.makedirs(folder, exist_ok=True)

    filename = f"{payload.seq}_{uuid.uuid4().hex[:8]}.{ext}"
    full_path = os.path.join(folder, filename)

    with open(full_path, "wb") as f:
        f.write(base64.b64decode(payload.image.base64))

    return os.path.join(day_folder, filename)


def _get_or_create_sku(db: Session, payload: IncomingResult) -> Sku:
    sku = db.query(Sku).filter(Sku.device_sku_id == payload.skuId).one_or_none()
    if sku is None:
        sku = Sku(device_sku_id=payload.skuId, code=payload.sku, name=None, shape=None)
        db.add(sku)
        db.flush()  # get sku.id without a full commit
    return sku


def store_incoming_result(db: Session, payload: IncomingResult) -> InspectionEvent:
    """Validates already done by pydantic. Persists one inspection event.
    Idempotent-ish: if this exact (device, seq) was already stored, skip it
    (guards against the device retrying a send after a dropped ack)."""
    existing = (
        db.query(InspectionEvent)
        .filter(InspectionEvent.device == payload.device, InspectionEvent.device_seq == payload.seq)
        .one_or_none()
    )
    if existing is not None:
        return existing

    sku = _get_or_create_sku(db, payload)
    image_path = _save_image(payload)
    shift_number, shift_date = compute_shift(payload.tsUtc)

    event = InspectionEvent(
        device=payload.device,
        device_seq=payload.seq,
        ts_utc=payload.tsUtc,
        verdict=payload.verdict.upper(),
        sku_id=sku.id,
        qty=payload.qty,
        score=payload.score,
        shift_number=shift_number,
        shift_business_date=shift_date,
        image_path=image_path,
        raw_payload=json.dumps(payload.model_dump(mode="json")),
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    return event
