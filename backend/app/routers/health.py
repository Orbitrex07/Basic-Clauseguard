from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.core.config import settings
from app.db.session import get_db
from app.schemas.health import HealthResponse

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
def health_check(db: Session = Depends(get_db)):
    db_status = "connected"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"error: {str(e)}"

    # Check if models are loaded in real mode
    models_loaded = False
    if settings.ML_MODE == "real":
        try:
            from app.services.classifier import classifier_service
            from app.services.extractor import extractor_service
            models_loaded = classifier_service.is_loaded() and extractor_service.is_loaded()
        except Exception:
            models_loaded = False
    else:
        # In mock mode, mock models are ready
        models_loaded = True

    return HealthResponse(
        status="ok" if db_status == "connected" else "degraded",
        ml_mode=settings.ML_MODE,
        models_loaded=models_loaded,
        database_status=db_status,
        version=settings.VERSION,
        disclaimer="This tool is informational and is not legal advice."
    )
