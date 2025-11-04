from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, crud
from app.database import get_db

router = APIRouter(prefix="/seasons", tags=["seasons"])

@router.get("/current", response_model=schemas.Season)
def get_current_season(
    db: Session = Depends(get_db)
):
    """Get the current (most recent) season"""
    season = crud.get_current_season(db)
    if not season:
        raise HTTPException(status_code=404, detail="No seasons found")
    return season