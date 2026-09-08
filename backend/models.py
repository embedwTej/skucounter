import datetime as dt

from sqlalchemy import (
    Boolean,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Sku(Base):
    """A part type the station is configured to recognize."""

    __tablename__ = "sku"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    # The device's own numeric id for this SKU (skuId in the payload).
    device_sku_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True)  # e.g. "PLATE-SQ45" / "SKU-001"
    name: Mapped[str | None] = mapped_column(String(128), nullable=True)  # e.g. "70gms Onion Chicken"
    shape: Mapped[str | None] = mapped_column(String(32), nullable=True)  # circle/square/triangle/hexagon etc.

    events: Mapped[list["InspectionEvent"]] = relationship(back_populates="sku")


class InspectionEvent(Base):
    """
    One inspected part, as pushed by the device over the websocket.
    Append-only: never updated or deleted. This table is the single
    source of truth that every report/dashboard number is derived from.
    """

    __tablename__ = "inspection_event"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device: Mapped[str | None] = mapped_column(String(128), nullable=True)
    device_seq: Mapped[int] = mapped_column(Integer, index=True)  # 'seq' from payload, for de-dup / ordering
    ts_utc: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), index=True)

    verdict: Mapped[str] = mapped_column(String(16), index=True)  # "PASS" / "FAIL"
    sku_id: Mapped[int] = mapped_column(ForeignKey("sku.id"), index=True)
    qty: Mapped[int] = mapped_column(Integer, default=1)
    score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Derived + stored at insert time so reports don't need timezone math
    # per-row on every query.
    shift_number: Mapped[int] = mapped_column(Integer, index=True)  # 1 or 2
    shift_business_date: Mapped[dt.date] = mapped_column(index=True)  # the "shift day" this event belongs to

    # Image handling: only ever a relative file path, never the blob itself.
    image_path: Mapped[str | None] = mapped_column(String(512), nullable=True)

    # Raw payload retained for troubleshooting / re-processing if the
    # schema evolves. Not used by reports.
    raw_payload: Mapped[str | None] = mapped_column(Text, nullable=True)

    sku: Mapped["Sku"] = relationship(back_populates="events")


class ResetLog(Base):
    """
    Audit trail of 'zero the live counters' actions. Historical events in
    InspectionEvent are never touched by a reset -- 'current' counts are
    simply computed as events since the latest reset row here.
    """

    __tablename__ = "reset_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ts_utc: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), index=True)
    note: Mapped[str | None] = mapped_column(String(256), nullable=True)
    source: Mapped[str] = mapped_column(String(32), default="api")


class DeviceConnection(Base):
    """Lightweight log of websocket connect/disconnect, for the Camera Status indicator."""

    __tablename__ = "device_connection"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    device: Mapped[str | None] = mapped_column(String(128), nullable=True)
    connected: Mapped[bool] = mapped_column(Boolean)
    ts_utc: Mapped[dt.datetime] = mapped_column(DateTime(timezone=True), index=True)
