import datetime as dt

from pydantic import BaseModel, Field


class IncomingImage(BaseModel):
    mime: str = "image/jpeg"
    width: int | None = None
    height: int | None = None
    bytes: int | None = None
    base64: str | None = None


class IncomingResult(BaseModel):
    """
    Shape of one JSON message pushed by the device over the websocket.
    Mirrors the 'results' item in the PartCount Integration API doc.

    NOTE: this is my best guess based on the REST payload you shared,
    since I don't have a sample of the actual push message yet. If the
    real websocket payload differs (extra fields, nested/batched, etc.),
    send me one real example and I'll adjust this in five minutes --
    everything downstream reads from this model, so that's the only
    place a schema change needs to happen.
    """

    device: str | None = None
    seq: int
    tsUtc: dt.datetime
    verdict: str
    sku: str
    skuId: int
    qty: int = 1
    score: float | None = None
    image: IncomingImage | None = None


# ---- REST response shapes (used by the dashboard/report endpoints) ----


class SkuCount(BaseModel):
    sku_code: str
    sku_name: str | None
    shape: str | None
    count: int
    pct_of_total: float


class DashboardResponse(BaseModel):
    total_count: int
    skus_detected: int
    current_shift: int
    current_shift_label: str
    last_updated: dt.datetime | None
    camera_connected: bool
    sku_counts: list[SkuCount]


class DateWiseRow(BaseModel):
    report_date: dt.date
    shift1_count: int
    shift2_count: int
    total_count: int


class DateWiseResponse(BaseModel):
    rows: list[DateWiseRow]
    total_shift1: int
    total_shift2: int
    grand_total: int


class SkuWiseRow(BaseModel):
    sku_code: str
    sku_name: str | None
    shape: str | None
    shift1_count: int
    shift2_count: int
    total_count: int


class SkuWiseResponse(BaseModel):
    rows: list[SkuWiseRow]
    total_shift1: int
    total_shift2: int
    grand_total: int


class ResetRequest(BaseModel):
    note: str | None = None


class ResetCountRow(BaseModel):
    sku_code: str
    current: int
    today: int


class ResetResponse(BaseModel):
    reset: bool
    ts_utc: dt.datetime
    source: str = "api"
    counts: list[ResetCountRow]
