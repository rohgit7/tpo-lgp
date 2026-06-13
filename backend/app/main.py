from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.upload import router as upload_router
from app.routes.anomalies import router as anomalies_router
from app.routes.summary import router as summary_router
from app.routes.chat import router as chat_router
from app.routes.visualize import router as visualize_router


from app.database.db import engine
from app.database.models import Base

Base.metadata.create_all(
    bind=engine
)

app = FastAPI(
    title="Shakun AI",
    description="Financial Forensics and Anomaly Detection Platform",
    version="1.0.0"
)


# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # React Vite
        "http://127.0.0.1:5173",
        "http://localhost:3000",  # React/Next.js
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Register Routes
app.include_router(upload_router)
app.include_router(anomalies_router)
app.include_router(summary_router)
app.include_router(chat_router)
app.include_router(visualize_router)


@app.get("/")
async def root():
    return {
        "message": "Welcome to Shakun AI",
        "status": "running",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy"
    }