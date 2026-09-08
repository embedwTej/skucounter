import datetime as dt

from sqlalchemy import func
from sqlalchemy.orm import Session

from models import DeviceConnection, InspectionEvent, ResetLog, Sku
from schemas import (
    DashboardResponse,
    DateWiseResponse,
    DateWiseRow,
    ResetCountRow,
    SkuCount,
    SkuWiseResponse,
    SkuWiseRow,
)
from shift_utils import compute_shift

PASS = "PASS"


def _latest_reset_ts(db: Session) -> dt.datetime | None:
    row = db.query(ResetLog).order_by(ResetLog.ts_utc.desc()).first()
    return row.ts_utc if row else None


def get_dashboard(db: Session) -> DashboardResponse:
    since = _latest_reset_ts(db)

    q = db.query(InspectionEvent).filter(InspectionEvent.verdict == PASS)
    if since:
        q = q.filter(InspectionEvent.ts_utc >= since)

    per_sku = (
        db.query(Sku.code, Sku.name, Sku.shape, func.sum(InspectionEvent.qty).label("cnt"))
        .join(InspectionEvent, InspectionEvent.sku_id == Sku.id)
        .filter(InspectionEvent.verdict == PASS)
    )
    if since:
        per_sku = per_sku.filter(InspectionEvent.ts_utc >= since)
    per_sku = per_sku.group_by(Sku.id).all()

    total = sum(r.cnt for r in per_sku) or 0
    sku_counts = [
        SkuCount(
            sku_code=r.code,
            sku_name=r.name,
            shape=r.shape,
            count=int(r.cnt),
            pct_of_total=round((r.cnt / total * 100), 1) if total else 0.0,
        )
        for r in per_sku
    ]

    last_event = db.query(InspectionEvent).order_by(InspectionEvent.ts_utc.desc()).first()
    now_utc = dt.datetime.now(dt.timezone.utc)
    current_shift, _ = compute_shift(now_utc)

    last_conn = db.query(DeviceConnection).order_by(DeviceConnection.ts_utc.desc()).first()
    camera_connected = bool(last_conn.connected) if last_conn else False

    return DashboardResponse(
        total_count=total,
        skus_detected=len(sku_counts),
        current_shift=current_shift,
        current_shift_label="07:00 AM - 07:00 PM" if current_shift == 1 else "07:00 PM - 07:00 AM",
        last_updated=last_event.ts_utc if last_event else None,
        camera_connected=camera_connected,
        sku_counts=sku_counts,
    )


def get_date_wise_report(
    db: Session, from_date: dt.date, to_date: dt.date, shift: int | None = None
) -> DateWiseResponse:
    q = (
        db.query(
            InspectionEvent.shift_business_date,
            InspectionEvent.shift_number,
            func.sum(InspectionEvent.qty).label("cnt"),
        )
        .filter(InspectionEvent.verdict == PASS)
        .filter(InspectionEvent.shift_business_date >= from_date)
        .filter(InspectionEvent.shift_business_date <= to_date)
    )
    if shift in (1, 2):
        q = q.filter(InspectionEvent.shift_number == shift)
    q = q.group_by(InspectionEvent.shift_business_date, InspectionEvent.shift_number)

    by_date: dict[dt.date, dict[int, int]] = {}
    for row in q.all():
        by_date.setdefault(row.shift_business_date, {})[row.shift_number] = int(row.cnt)

    rows = []
    for d in sorted(by_date.keys(), reverse=True):
        s1 = by_date[d].get(1, 0)
        s2 = by_date[d].get(2, 0)
        rows.append(DateWiseRow(report_date=d, shift1_count=s1, shift2_count=s2, total_count=s1 + s2))

    return DateWiseResponse(
        rows=rows,
        total_shift1=sum(r.shift1_count for r in rows),
        total_shift2=sum(r.shift2_count for r in rows),
        grand_total=sum(r.total_count for r in rows),
    )


def get_sku_wise_report(
    db: Session,
    from_date: dt.date,
    to_date: dt.date,
    shift: int | None = None,
    sku_code: str | None = None,
) -> SkuWiseResponse:
    q = (
        db.query(
            Sku.code,
            Sku.name,
            Sku.shape,
            InspectionEvent.shift_number,
            func.sum(InspectionEvent.qty).label("cnt"),
        )
        .join(InspectionEvent, InspectionEvent.sku_id == Sku.id)
        .filter(InspectionEvent.verdict == PASS)
        .filter(InspectionEvent.shift_business_date >= from_date)
        .filter(InspectionEvent.shift_business_date <= to_date)
    )
    if shift in (1, 2):
        q = q.filter(InspectionEvent.shift_number == shift)
    if sku_code:
        q = q.filter(Sku.code == sku_code)
    q = q.group_by(Sku.id, InspectionEvent.shift_number)

    by_sku: dict[str, dict] = {}
    for row in q.all():
        entry = by_sku.setdefault(row.code, {"name": row.name, "shape": row.shape, 1: 0, 2: 0})
        entry[row.shift_number] = int(row.cnt)

    rows = []
    for code, v in by_sku.items():
        s1, s2 = v.get(1, 0), v.get(2, 0)
        rows.append(
            SkuWiseRow(sku_code=code, sku_name=v["name"], shape=v["shape"], shift1_count=s1, shift2_count=s2, total_count=s1 + s2)
        )
    rows.sort(key=lambda r: r.total_count, reverse=True)

    return SkuWiseResponse(
        rows=rows,
        total_shift1=sum(r.shift1_count for r in rows),
        total_shift2=sum(r.shift2_count for r in rows),
        grand_total=sum(r.total_count for r in rows),
    )


def reset_counts(db: Session, note: str | None) -> list[ResetCountRow]:
    now_utc = dt.datetime.now(dt.timezone.utc)
    today_local, _ = compute_shift(now_utc)  # not used directly, just to confirm tz is loaded
    today_date = now_utc.date()

    # "today" totals (survive the reset) computed BEFORE inserting the new reset row.
    today_counts = (
        db.query(Sku.code, func.sum(InspectionEvent.qty).label("cnt"))
        .join(InspectionEvent, InspectionEvent.sku_id == Sku.id)
        .filter(InspectionEvent.verdict == PASS)
        .filter(InspectionEvent.shift_business_date == today_date)
        .group_by(Sku.id)
        .all()
    )
    today_map = {r.code: int(r.cnt) for r in today_counts}

    db.add(ResetLog(ts_utc=now_utc, note=note, source="api"))
    db.commit()

    all_skus = db.query(Sku.code).all()
    return [ResetCountRow(sku_code=s.code, current=0, today=today_map.get(s.code, 0)) for s in all_skus]
