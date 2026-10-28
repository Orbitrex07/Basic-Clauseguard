from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import logger

from app.db.init_db import init_db
from app.db.session import SessionLocal

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION} in {settings.ML_MODE} mode.")
    try:
        db = SessionLocal()
        init_db(db)
        db.close()
    except Exception as e:
        logger.error(f"Error during init_db: {e}")
    yield
    logger.info(f"Shutting down {settings.PROJECT_NAME}.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="ClauseGuard — AI-Based Contract Clause Extraction and Risk Flagging System. This tool is informational and is not legal advice.",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS Middleware
origins = settings.CORS_ORIGINS if isinstance(settings.CORS_ORIGINS, list) else [settings.CORS_ORIGINS]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers import health, auth, documents, clauses, reports, admin

# Include core routers
app.include_router(health.router, prefix=settings.API_V1_STR)
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(documents.router, prefix=settings.API_V1_STR)
app.include_router(clauses.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "message": "Welcome to ClauseGuard API",
        "disclaimer": "This tool is informational and is not legal advice.",
        "docs": f"{settings.API_V1_STR}/docs",
        "health": f"{settings.API_V1_STR}/health"
    }
