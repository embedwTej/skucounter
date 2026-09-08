"""
Central configuration. Values can be overridden with environment variables,
e.g. on Windows (PowerShell):
    $env:DATABASE_URL = "postgresql+psycopg2://user:pass@localhost:5432/sku_counter"
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # --- Database -----------------------------------------------------
    database_url: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/sku_counter"

    # --- Websocket ingestion -------------------------------------------
    ws_ingest_path: str = "/ws/ingest"
    # Optional shared-secret check for the device connection.
    # Leave blank to disable (fine for a trusted LAN / first pass).
    ws_shared_secret: str = ""

    # --- Images ----------------------------------------------------------
    # Where inspection images are written on disk. A relative path in the
    # DB is stored under this root, so the folder can be moved/mounted
    # without needing a DB migration.
    image_storage_root: str = "./images"
    # Off for now per your instruction -- flip to True later and the
    # ingest path (ingest_service._save_image) is already wired for it.
    store_images: bool = False

    # --- Shift configuration ---------------------------------------------
    # 24h "HH:MM" boundaries. Shift 1 runs [shift1_start, shift2_start),
    # Shift 2 runs [shift2_start, shift1_start) and crosses midnight.
    shift1_start: str = "07:00"
    shift2_start: str = "19:00"
    timezone: str = "Asia/Kolkata"

    # --- Server ------------------------------------------------------------
    host: str = "0.0.0.0"
    port: int = 8000

    class Config:
        env_file = ".env"


settings = Settings()
