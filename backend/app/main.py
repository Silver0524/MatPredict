from fastapi import FastAPI
from app.database import engine, Base
from app import models

# Create all tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Wrestling Predictor API")

@app.get("/")
def read_root():
    return {"message": "Wrestling Predictor API"}