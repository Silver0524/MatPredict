from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from app import schemas, crud
from app.database import get_db
from app.ml.predictor import get_predictor
from app.ml import features

router = APIRouter(prefix="/predictions", tags=["predictions"])

@router.post("/", response_model=schemas.PredictionResponse)
def predict_match(
    request: schemas.PredictionRequest,
    db: Session = Depends(get_db)
):
    """
    Predict the outcome of a match between two wrestlers
    """
    # Validate wrestlers exist
    wrestler1 = crud.get_wrestler(db, request.wrestler1_id)
    wrestler2 = crud.get_wrestler(db, request.wrestler2_id)
    
    if not wrestler1:
        raise HTTPException(status_code=404, detail=f"Wrestler {request.wrestler1_id} not found")
    if not wrestler2:
        raise HTTPException(status_code=404, detail=f"Wrestler {request.wrestler2_id} not found")
    
    # Validate season if provided
    if request.season_id:
        season = crud.get_season(db, request.season_id)
        if not season:
            raise HTTPException(status_code=404, detail=f"Season {request.season_id} not found")
    
    # Validate weight class if provided
    if request.weight_class_id:
        weight_class = crud.get_weight_class(db, request.weight_class_id)
        if not weight_class:
            raise HTTPException(status_code=404, detail=f"Weight class {request.weight_class_id} not found")
    
    try:
        # Compute features for wrestler 1 (from their perspective)
        w1_features = features.compute_wrestler_features(
            db, 
            request.wrestler1_id,
            season_id=request.season_id,
            weight_class_id=request.weight_class_id
        )
        
        # Compute features for wrestler 2 (for comparison/display)
        w2_features = features.compute_wrestler_features(
            db, 
            request.wrestler2_id,
            season_id=request.season_id,
            weight_class_id=request.weight_class_id
        )
        
        # Load predictor and make prediction
        predictor = get_predictor()
        
        # Use wrestler1's features for prediction
        wrestler1_win_prob, wrestler2_win_prob = predictor.predict(w1_features)
        
        # Determine predicted winner
        predicted_winner_id = request.wrestler1_id if wrestler1_win_prob > wrestler2_win_prob else request.wrestler2_id
        confidence = max(wrestler1_win_prob, wrestler2_win_prob)
        
        # Get H2H stats
        h2h = crud.get_h2h_stats(db, request.wrestler1_id, request.wrestler2_id)
        
        # Compile features for response (both wrestlers for comparison)
        features_response = {
            'wrestler1': w1_features,
            'wrestler2': w2_features,
            'h2h_total_matches': len(db.query(crud.models.Match).filter(
                crud.or_(
                    crud.and_(crud.models.Match.wrestler1_id == request.wrestler1_id, 
                             crud.models.Match.wrestler2_id == request.wrestler2_id),
                    crud.and_(crud.models.Match.wrestler1_id == request.wrestler2_id, 
                             crud.models.Match.wrestler2_id == request.wrestler1_id)
                )
            ).all())
        }
        
        return schemas.PredictionResponse(
            wrestler1_id=request.wrestler1_id,
            wrestler2_id=request.wrestler2_id,
            wrestler1_name=wrestler1.name,
            wrestler2_name=wrestler2.name,
            wrestler1_win_probability=float(wrestler1_win_prob),
            wrestler2_win_probability=float(wrestler2_win_prob),
            predicted_winner_id=predicted_winner_id,
            confidence=float(confidence),
            h2h_stats=h2h,
            features=features_response
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error computing features: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error making prediction: {str(e)}"
        )

@router.get("/compare/{wrestler1_id}/{wrestler2_id}")
def compare_wrestlers(
    wrestler1_id: int,
    wrestler2_id: int,
    season_id: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Compare two wrestlers' statistics side by side
    """
    # Validate wrestlers exist
    wrestler1 = crud.get_wrestler(db, wrestler1_id)
    wrestler2 = crud.get_wrestler(db, wrestler2_id)
    
    if not wrestler1:
        raise HTTPException(status_code=404, detail=f"Wrestler {wrestler1_id} not found")
    if not wrestler2:
        raise HTTPException(status_code=404, detail=f"Wrestler {wrestler2_id} not found")
    
    # Get features for both wrestlers
    features1 = crud.get_wrestler_features(db, wrestler1_id, season_id=season_id)
    features2 = crud.get_wrestler_features(db, wrestler2_id, season_id=season_id)
    
    # Get H2H stats
    h2h = crud.get_h2h_stats(db, wrestler1_id, wrestler2_id)
    
    # Compute live features for comparison
    try:
        w1_live_features = features.compute_wrestler_features(
            db, wrestler1_id, season_id=season_id
        )
        w2_live_features = features.compute_wrestler_features(
            db, wrestler2_id, season_id=season_id
        )
        
        comparison = {
            "win_rate_diff": w1_live_features['season_win_rate'] - w2_live_features['season_win_rate'],
            "experience_diff": w1_live_features['experience'] - w2_live_features['experience'],
            "streak_diff": w1_live_features['streak'] - w2_live_features['streak'],
            "form_diff_last_5": w1_live_features['win_rate_last_5'] - w2_live_features['win_rate_last_5'],
            "form_diff_last_10": w1_live_features['win_rate_last_10'] - w2_live_features['win_rate_last_10'],
            "scoring_diff_last_5": w1_live_features['avg_point_differential_last_5'] - w2_live_features['avg_point_differential_last_5'],
            "scoring_diff_last_10": w1_live_features['avg_point_differential_last_10'] - w2_live_features['avg_point_differential_last_10'],
        }
    except:
        # Fallback to stored features if live computation fails
        comparison = {
            "win_rate_diff": float(features1.season_win_rate or 0) - float(features2.season_win_rate or 0) if features1 and features2 else None,
            "experience_diff": (features1.experience or 0) - (features2.experience or 0) if features1 and features2 else None,
            "streak_diff": (features1.streak or 0) - (features2.streak or 0) if features1 and features2 else None,
            "form_diff_last_5": (float(features1.win_rate_last_5 or 0) - float(features2.win_rate_last_5 or 0)) if features1 and features2 else None,
            "scoring_diff_last_5": (float(features1.avg_point_differential_last_5 or 0) - float(features2.avg_point_differential_last_5 or 0)) if features1 and features2 else None,
        }
    
    return {
        "wrestler1": {
            "info": wrestler1,
            "features": features1
        },
        "wrestler2": {
            "info": wrestler2,
            "features": features2
        },
        "h2h_stats": h2h,
        "comparison": comparison
    }