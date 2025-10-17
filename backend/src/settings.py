import os
from typing import List

from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()


class Settings(BaseModel):
    # Application
    app_name: str = os.getenv("APP_NAME", "Interplayers API")
    app_version: str = os.getenv("APP_VERSION", "1.0.0")
    app_env: str = os.getenv("APP_ENV", "dev")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"

    # Database
    database_url: str = (
        os.getenv("DATABASE_URL",
                  "postgresql+psycopg://"
                  "postgres:postgres@localhost"
                  ":5432"
                  "/interplayers_db"))

    # CORS
    cors_origins: List[str] = os.getenv("CORS_ORIGINS",
                                        "http://localhost:4200,"
                                        "http://localhost:8080").split(
        ",")

    # Server
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))

    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")


settings = Settings()
