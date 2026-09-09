import datetime as dt

from pydantic import BaseModel, Field


class IncomingImage(BaseModel):
    mime: str = "image/jpeg"
    width: int | None = None
    height: int | None = None
    bytes: int | None = None
    base64: str | None = None


class IncomingResult(BaseModel):
    """Normalized single event used by the persistence layer."""

    device: str | None = None
    seq: int
    tsUtc: dt.datetime
    verdict: str
    sku: str
    skuId: int
    qty: int = 1
    score: float | None = None
    image: IncomingImage | None = None


class StationInfo(BaseModel):
    id: str
    name: str | None = None
    product: str | None = None
    version: str | None = None


class HelloMessage(BaseModel):
    type: str = "hello"
    protocol: int = 1
    station: StationInfo
    capabilities: list[str] = Field(default_factory=list)
    retentionDays: int | None = None
    local: dict = Field(default_factory=dict)


class SkuDefinition(BaseModel):
    id: int
    name: str
    active: bool = True
    deleted: bool = False
    minScore: float | None = None


class SkuMessage(BaseModel):
    type: str = "skus"
    skus: list[SkuDefinition] = Field(default_factory=list)


class EventRecord(BaseModel):
    id: int
    ts: dt.datetime
    date: dt.date
    skuId: int
    sku: str
    qty: int = 1
    score: float | None = None


class EventsMessage(BaseModel):
    type: str = "events"
    replayId: str | None = None
    events: list[EventRecord] = Field(default_factory=list)
    cursor: int
    hasMore: bool = False


class ResetRecord(BaseModel):
    id: int
    ts: dt.datetime
    source: str
    note: str | None = None


class ResetsMessage(BaseModel):
    type: str = "resets"
    replayId: str | None = None
    resets: list[ResetRecord] = Field(default_factory=list)
    cursor: int
    hasMore: bool = False


class ImagesMessage(BaseModel):
    type: str = "images"
    replayId: str | None = None
    images: list[dict] = Field(default_factory=list)
    cursor: int
    hasMore: bool = False
    gap: bool = False
    skipped: int = 0


class StatusMessage(BaseModel):
    type: str = "status"
    model_config = {"extra": "allow"}


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
