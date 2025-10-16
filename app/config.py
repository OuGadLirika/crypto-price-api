from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass(frozen=True)
class AppConfig:
    database_url: str
    host: str = "0.0.0.0"
    port: int = 8000
    page_size: int = 10
    enable_uvloop: bool = True
    env: str = "development"
    run_create_all: bool = True

    @staticmethod
    def load(env_file: Optional[str] = None) -> "AppConfig":
        load_dotenv(env_file)
        database_url = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/qorpo")
        host = os.getenv("HOST", "0.0.0.0")
        port = int(os.getenv("PORT", "8000"))
        page_size = int(os.getenv("PAGE_SIZE", "10"))
        enable_uvloop = os.getenv("ENABLE_UVLOOP", "true").lower() in {"1", "true", "yes"}
        env = os.getenv("ENV", "development").lower()
        run_create_all = os.getenv("RUN_CREATE_ALL", "").lower() in {"1", "true", "yes"}
        return AppConfig(
            database_url=database_url,
            host=host,
            port=port,
            page_size=page_size,
            enable_uvloop=enable_uvloop,
            env=env,
            run_create_all=run_create_all,
        )
