from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app import models
from app.api import wrestlers, predictions, seasons

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Wrestling Predictor API",
    description="API for predicting NCAA wrestling match outcomes",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.js default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with /api prefix
app.include_router(wrestlers.router, prefix="/api")
app.include_router(predictions.router, prefix="/api")
app.include_router(seasons.router, prefix="/api")

@app.get("/")
def read_root():
    return {
        "message": "Wrestling Predictor API",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}