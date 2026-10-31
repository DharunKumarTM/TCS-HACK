import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database.connection import init_db, SessionLocal
from app.api.routes import router as api_router
from app.services.project_service import project_service

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("archmind.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Initializing ArchMind AI database schema...")
    init_db()
    
    # Auto-seed SmartBank Demo project if database is fresh
    db = SessionLocal()
    try:
        from app.database.models import Project
        count = db.query(Project).count()
        if count == 0:
            logger.info("Fresh database detected. Pre-seeding SmartBank reference project...")
            project_service.load_demo_smartbank_project(db)
            logger.info("SmartBank project seeded successfully.")
    except Exception as e:
        logger.warning(f"Could not auto-seed SmartBank project on startup: {e}")
    finally:
        db.close()
        
    yield
    logger.info("ArchMind AI backend shutting down.")

app = FastAPI(
    title="ArchMind AI – Evidence-Driven Agentic Software Architect",
    description=(
        "TCS AI Hackathon Challenge 02: Transforming fragmented, incomplete and contradictory "
        "software requirements into explainable, validated and traceable software architecture "
        "powered by LangGraph orchestration, Docling/LlamaIndex RAG, and Gemini API reasoning."
    ),
    version="1.0.0",
    lifespan=lifespan
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routes
app.include_router(api_router)

@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "database": "configured",
        "gemini_live": settings.GEMINI_API_KEY != "" and settings.GEMINI_API_KEY != "your-gemini-api-key-here"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.PORT, reload=True)

