from pydantic import BaseModel
from typing import Optional


class HealthResponse(BaseModel):
    status: str
    ml_mode: str
    models_loaded: bool
    database_status: str
    version: str
    disclaimer: str = "This tool is informational and is not legal advice."
