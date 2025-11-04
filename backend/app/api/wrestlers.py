from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app import schemas, crud
from app.database import get_db

router = APIRouter(prefix="/wrestlers", tags=["wrestlers"])

@router.get("/", response_model=List[schemas.Wrestler])
def list_wrestlers(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db)
):
    """Get all wrestlers"""
    wrestlers = crud.get_wrestlers(db, skip=skip, limit=limit)
    return wrestlers

@router.get("/search", response_model=List[schemas.Wrestler])
def search_wrestlers(
    q: str, 
    db: Session = Depends(get_db)
):
    """Search wrestlers by name"""
    wrestlers = crud.search_wrestlers(db, q)
    return wrestlers

@router.get("/{wrestler_id}", response_model=schemas.Wrestler)
def get_wrestler(
    wrestler_id: int, 
    db: Session = Depends(get_db)
):
    """Get wrestler by ID"""
    wrestler = crud.get_wrestler(db, wrestler_id)
    if not wrestler:
        raise HTTPException(status_code=404, detail="Wrestler not found")
    return wrestler

@router.get("/{wrestler_id}/matches", response_model=List[schemas.MatchWithDetails])
def get_wrestler_matches(
    wrestler_id: int, 
    season_id: Optional[int] = None,
    limit: int = 20, 
    db: Session = Depends(get_db)
):
    """Get matches for a wrestler, optionally filtered by season"""
    wrestler = crud.get_wrestler(db, wrestler_id)
    if not wrestler:
        raise HTTPException(status_code=404, detail="Wrestler not found")
    
    matches = crud.get_wrestler_matches(db, wrestler_id, season_id=season_id, limit=limit)
    return matches

@router.get("/{wrestler_id}/stats")
def get_wrestler_stats(
    wrestler_id: int, 
    season_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """Get wrestler statistics, optionally filtered by season"""
    wrestler = crud.get_wrestler(db, wrestler_id)
    if not wrestler:
        raise HTTPException(status_code=404, detail="Wrestler not found")
    
    features = crud.get_wrestler_features(db, wrestler_id, season_id=season_id)
    
    if not features:
        return {
            "wrestler": wrestler,
            "season_id": season_id,
            "stats": {
                "career_matches": 0,
                "career_wins": 0,
                "career_losses": 0,
                "season_matches": 0,
                "season_wins": 0,
                "season_win_rate": 0.0,
                "win_rate_last_5": None,
                "win_rate_last_10": None,
            }
        }
    
    return {
        "wrestler": wrestler,
        "season_id": season_id,
        "stats": {
            # Career stats
            "career_matches": features.career_matches,
            "career_wins": features.career_wins,
            "career_losses": features.career_losses,
            
            # Season stats
            "season_matches": features.season_matches,
            "season_wins": features.season_wins,
            "season_win_rate": float(features.season_win_rate) if features.season_win_rate else 0.0,
            
            # Recent form
            "win_rate_last_5": float(features.win_rate_last_5) if features.win_rate_last_5 else None,
            "win_rate_last_10": float(features.win_rate_last_10) if features.win_rate_last_10 else None,
            "win_rate_last_15": float(features.win_rate_last_15) if features.win_rate_last_15 else None,
            "streak": features.streak,
            
            # Match quality
            "bonus_win_rate_last_5": float(features.bonus_win_rate_last_5) if features.bonus_win_rate_last_5 else None,
            "bonus_win_rate_last_10": float(features.bonus_win_rate_last_10) if features.bonus_win_rate_last_10 else None,
            
            # Scoring
            "avg_points_scored_last_5": float(features.avg_points_scored_last_5) if features.avg_points_scored_last_5 else None,
            "avg_points_allowed_last_5": float(features.avg_points_allowed_last_5) if features.avg_points_allowed_last_5 else None,
            "avg_point_differential_last_5": float(features.avg_point_differential_last_5) if features.avg_point_differential_last_5 else None,
            
            # Competition format
            "dual_meet_win_rate": float(features.dual_meet_win_rate) if features.dual_meet_win_rate else None,
            "tournament_win_rate": float(features.tournament_win_rate) if features.tournament_win_rate else None,
            "weight_class_win_rate": float(features.weight_class_win_rate) if features.weight_class_win_rate else None,
            
            # Activity
            "days_since_last_match": features.days_since_last_match,
            "matches_per_week_last_30_days": float(features.matches_per_week_last_30_days) if features.matches_per_week_last_30_days else None,
        }
    }