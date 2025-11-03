from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, or_
from app import models
from typing import Dict, Optional, Tuple, List
import numpy as np
from datetime import datetime, timedelta

def get_recent_matches(db: Session, wrestler_id: int, season_id: Optional[int] = None, n: int = 10):
    """Get n most recent matches for a wrestler"""
    query = db.query(models.Match).filter(
        or_(
            models.Match.wrestler1_id == wrestler_id,
            models.Match.wrestler2_id == wrestler_id
        )
    )
    
    if season_id:
        query = query.filter(models.Match.season_id == season_id)
    
    matches = query.order_by(desc(models.Match.date)).limit(n).all()
    
    return matches

def calculate_win_rate(matches: List[models.Match], wrestler_id: int) -> float:
    """Calculate win rate from list of matches"""
    if not matches:
        return 0.0
    
    wins = sum(1 for m in matches if m.winner_id == wrestler_id)
    return wins / len(matches)

def calculate_avg_point_diff(matches: List[models.Match], wrestler_id: int) -> float:
    """Calculate average point differential"""
    if not matches:
        return 0.0
    
    diffs = []
    for match in matches:
        if match.wrestler1_score is None or match.wrestler2_score is None:
            continue
            
        if match.wrestler1_id == wrestler_id:
            diffs.append(match.wrestler1_score - match.wrestler2_score)
        else:
            diffs.append(match.wrestler2_score - match.wrestler1_score)
    
    return np.mean(diffs) if diffs else 0.0

def calculate_avg_points_scored(matches: List[models.Match], wrestler_id: int) -> float:
    """Calculate average points scored"""
    if not matches:
        return 0.0
    
    scores = []
    for match in matches:
        if match.wrestler1_score is None or match.wrestler2_score is None:
            continue
            
        if match.wrestler1_id == wrestler_id:
            scores.append(match.wrestler1_score)
        else:
            scores.append(match.wrestler2_score)
    
    return np.mean(scores) if scores else 0.0

def calculate_avg_points_allowed(matches: List[models.Match], wrestler_id: int) -> float:
    """Calculate average points allowed"""
    if not matches:
        return 0.0
    
    allowed = []
    for match in matches:
        if match.wrestler1_score is None or match.wrestler2_score is None:
            continue
            
        if match.wrestler1_id == wrestler_id:
            allowed.append(match.wrestler2_score)
        else:
            allowed.append(match.wrestler1_score)
    
    return np.mean(allowed) if allowed else 0.0

def get_result_type_rates(db: Session, matches: List[models.Match], wrestler_id: int) -> Dict[str, float]:
    """Calculate rates of different result types (pins, tech falls, major decisions)"""
    if not matches:
        return {'pin_rate': 0.0, 'tech_fall_rate': 0.0, 'major_decision_rate': 0.0}
    
    wins = [m for m in matches if m.winner_id == wrestler_id]
    total_wins = len(wins)
    
    if total_wins == 0:
        return {'pin_rate': 0.0, 'tech_fall_rate': 0.0, 'major_decision_rate': 0.0}
    
    # Get result type codes
    result_type_ids = [m.result_type_id for m in wins]
    result_types = db.query(models.ResultType).filter(
        models.ResultType.id.in_(result_type_ids)
    ).all()
    
    result_type_map = {rt.id: rt.code for rt in result_types}
    
    pins = sum(1 for m in wins if result_type_map.get(m.result_type_id, '').upper() in ['PIN', 'FALL'])
    tech_falls = sum(1 for m in wins if result_type_map.get(m.result_type_id, '').upper() in ['TF', 'TECH'])
    major_decisions = sum(1 for m in wins if result_type_map.get(m.result_type_id, '').upper() in ['MD', 'MAJ'])
    
    return {
        'pin_rate': pins / total_wins,
        'tech_fall_rate': tech_falls / total_wins,
        'major_decision_rate': major_decisions / total_wins
    }

def calculate_bonus_win_rate(db: Session, matches: List[models.Match], wrestler_id: int) -> float:
    """Calculate bonus win rate (pins, tech falls, major decisions)"""
    if not matches:
        return 0.0
    
    wins = [m for m in matches if m.winner_id == wrestler_id]
    if not wins:
        return 0.0
    
    # Get result type codes
    result_type_ids = [m.result_type_id for m in wins]
    result_types = db.query(models.ResultType).filter(
        models.ResultType.id.in_(result_type_ids)
    ).all()
    
    result_type_map = {rt.id: rt.code for rt in result_types}
    
    bonus_wins = sum(1 for m in wins if result_type_map.get(m.result_type_id, '').upper() in 
                     ['PIN', 'FALL', 'TF', 'TECH', 'MD', 'MAJ'])
    
    return bonus_wins / len(wins)

def calculate_close_match_win_rate(matches: List[models.Match], wrestler_id: int) -> float:
    """Calculate win rate in close matches (within 3 points)"""
    if not matches:
        return 0.0
    
    close_matches = []
    for match in matches:
        if match.wrestler1_score is None or match.wrestler2_score is None:
            continue
        
        point_diff = abs(match.wrestler1_score - match.wrestler2_score)
        if point_diff <= 3:
            close_matches.append(match)
    
    if not close_matches:
        return 0.0
    
    close_wins = sum(1 for m in close_matches if m.winner_id == wrestler_id)
    return close_wins / len(close_matches)

def calculate_overtime_rate(db: Session, matches: List[models.Match]) -> float:
    """Calculate overtime rate from matches"""
    if not matches:
        return 0.0
    
    match_ids = [m.id for m in matches]
    match_stats = db.query(models.MatchStats).filter(
        models.MatchStats.match_id.in_(match_ids)
    ).all()
    
    if not match_stats:
        return 0.0
    
    overtime_count = sum(1 for ms in match_stats if ms.duration_seconds and ms.duration_seconds > 420)
    return overtime_count / len(match_stats)

def calculate_avg_duration(db: Session, matches: List[models.Match]) -> float:
    """Calculate average match duration in seconds"""
    if not matches:
        return 0.0
    
    match_ids = [m.id for m in matches]
    match_stats = db.query(models.MatchStats).filter(
        models.MatchStats.match_id.in_(match_ids),
        models.MatchStats.duration_seconds.isnot(None)
    ).all()
    
    if not match_stats:
        return 0.0
    
    durations = [ms.duration_seconds for ms in match_stats if ms.duration_seconds]
    return np.mean(durations) if durations else 0.0

def get_dual_tournament_stats(db: Session, wrestler_id: int, season_id: Optional[int] = None) -> Dict[str, float]:
    """Calculate dual meet and tournament performance"""
    query = db.query(models.Match).filter(
        or_(
            models.Match.wrestler1_id == wrestler_id,
            models.Match.wrestler2_id == wrestler_id
        )
    )
    
    if season_id:
        query = query.filter(models.Match.season_id == season_id)
    
    all_matches = query.all()
    
    if not all_matches:
        return {
            'dual_meet_wins': 0,
            'dual_meet_matches': 0,
            'dual_meet_win_rate': 0.5,
            'tournament_wins': 0,
            'tournament_matches': 0,
            'tournament_win_rate': 0.5
        }
    
    dual_matches = [m for m in all_matches if m.meet_id is not None]
    tournament_matches = [m for m in all_matches if m.meet_id is None]
    
    dual_wins = sum(1 for m in dual_matches if m.winner_id == wrestler_id)
    tournament_wins = sum(1 for m in tournament_matches if m.winner_id == wrestler_id)
    
    return {
        'dual_meet_wins': dual_wins,
        'dual_meet_matches': len(dual_matches),
        'dual_meet_win_rate': dual_wins / len(dual_matches) if dual_matches else 0.5,
        'tournament_wins': tournament_wins,
        'tournament_matches': len(tournament_matches),
        'tournament_win_rate': tournament_wins / len(tournament_matches) if tournament_matches else 0.5
    }

def get_weight_class_stats(db: Session, wrestler_id: int, weight_class_id: int, season_id: Optional[int] = None) -> Dict[str, float]:
    """Calculate weight class specific performance"""
    query = db.query(models.Match).filter(
        or_(
            models.Match.wrestler1_id == wrestler_id,
            models.Match.wrestler2_id == wrestler_id
        ),
        models.Match.weight_class_id == weight_class_id
    )
    
    if season_id:
        query = query.filter(models.Match.season_id == season_id)
    
    matches = query.all()
    
    if not matches:
        return {
            'weight_class_matches': 0,
            'weight_class_wins': 0,
            'weight_class_win_rate': 0.5
        }
    
    wins = sum(1 for m in matches if m.winner_id == wrestler_id)
    
    return {
        'weight_class_matches': len(matches),
        'weight_class_wins': wins,
        'weight_class_win_rate': wins / len(matches) if matches else 0.5
    }

def calculate_days_since_last_match(db: Session, wrestler_id: int, reference_date: datetime) -> int:
    """Calculate days since wrestler's last match"""
    last_match = db.query(models.Match).filter(
        or_(
            models.Match.wrestler1_id == wrestler_id,
            models.Match.wrestler2_id == wrestler_id
        ),
        models.Match.date < reference_date
    ).order_by(desc(models.Match.date)).first()
    
    if not last_match:
        return 0
    
    return (reference_date - datetime.combine(last_match.date, datetime.min.time())).days

def calculate_matches_per_week(db: Session, wrestler_id: int, reference_date: datetime, window_days: int = 30) -> float:
    """Calculate matches per week over rolling window"""
    window_start = reference_date - timedelta(days=window_days)
    
    matches = db.query(models.Match).filter(
        or_(
            models.Match.wrestler1_id == wrestler_id,
            models.Match.wrestler2_id == wrestler_id
        ),
        models.Match.date >= window_start.date(),
        models.Match.date < reference_date.date()
    ).count()
    
    return matches * 7 / window_days

def get_career_stats(db: Session, wrestler_id: int, season_id: Optional[int] = None) -> Dict[str, int]:
    """Get career statistics for a wrestler"""
    query = db.query(models.Match).filter(
        or_(
            models.Match.wrestler1_id == wrestler_id,
            models.Match.wrestler2_id == wrestler_id
        )
    )
    
    if season_id:
        query = query.filter(models.Match.season_id == season_id)
    
    all_matches = query.all()
    
    if not all_matches:
        return {
            'career_matches': 0,
            'career_wins': 0,
            'career_losses': 0
        }
    
    wins = sum(1 for m in all_matches if m.winner_id == wrestler_id)
    
    return {
        'career_matches': len(all_matches),
        'career_wins': wins,
        'career_losses': len(all_matches) - wins
    }

def get_season_stats(db: Session, wrestler_id: int, season_id: int) -> Dict[str, float]:
    """Get season-specific statistics"""
    matches = db.query(models.Match).filter(
        or_(
            models.Match.wrestler1_id == wrestler_id,
            models.Match.wrestler2_id == wrestler_id
        ),
        models.Match.season_id == season_id
    ).all()
    
    if not matches:
        return {
            'season_matches': 0,
            'season_wins': 0,
            'season_win_rate': 0.0
        }
    
    wins = sum(1 for m in matches if m.winner_id == wrestler_id)
    
    return {
        'season_matches': len(matches),
        'season_wins': wins,
        'season_win_rate': wins / len(matches) if matches else 0.0
    }

def get_previous_season_win_rate(db: Session, wrestler_id: int, current_season_id: int) -> float:
    """Get previous season's win rate"""
    current_season = db.query(models.Season).filter(models.Season.id == current_season_id).first()
    if not current_season:
        return 0.5
    
    prev_season = db.query(models.Season).filter(
        models.Season.start_year == current_season.start_year - 1
    ).first()
    
    if not prev_season:
        return 0.5
    
    stats = get_season_stats(db, wrestler_id, prev_season.id)
    return stats.get('season_win_rate', 0.5)

def calculate_streak(db: Session, wrestler_id: int, season_id: Optional[int] = None) -> int:
    """Calculate current win/loss streak (positive for wins, negative for losses)"""
    query = db.query(models.Match).filter(
        or_(
            models.Match.wrestler1_id == wrestler_id,
            models.Match.wrestler2_id == wrestler_id
        )
    )
    
    if season_id:
        query = query.filter(models.Match.season_id == season_id)
    
    matches = query.order_by(desc(models.Match.date)).limit(20).all()
    
    if not matches:
        return 0
    
    streak = 0
    last_result = None
    
    for match in reversed(matches):
        is_win = match.winner_id == wrestler_id
        
        if last_result is None:
            last_result = is_win
            streak = 1
        elif last_result == is_win:
            streak += 1
        else:
            break
    
    return streak if last_result else -streak

def get_h2h_stats(db: Session, wrestler1_id: int, wrestler2_id: int) -> Tuple[int, int, int]:
    """Get head-to-head record (total_matches, wrestler1_wins, wrestler2_wins)"""
    matches = db.query(models.Match).filter(
        or_(
            and_(models.Match.wrestler1_id == wrestler1_id, models.Match.wrestler2_id == wrestler2_id),
            and_(models.Match.wrestler1_id == wrestler2_id, models.Match.wrestler2_id == wrestler1_id)
        )
    ).all()
    
    wrestler1_wins = sum(1 for m in matches if m.winner_id == wrestler1_id)
    wrestler2_wins = sum(1 for m in matches if m.winner_id == wrestler2_id)
    
    return len(matches), wrestler1_wins, wrestler2_wins

def compute_wrestler_features(
    db: Session, 
    wrestler_id: int, 
    season_id: Optional[int] = None,
    weight_class_id: Optional[int] = None,
    reference_date: Optional[datetime] = None
) -> Dict:
    """
    Compute all features for a single wrestler
    """
    if reference_date is None:
        reference_date = datetime.now()
    
    # Get matches for different windows
    matches_3 = get_recent_matches(db, wrestler_id, season_id, n=3)
    matches_5 = get_recent_matches(db, wrestler_id, season_id, n=5)
    matches_10 = get_recent_matches(db, wrestler_id, season_id, n=10)
    matches_15 = get_recent_matches(db, wrestler_id, season_id, n=15)
    
    # Career stats
    career_stats = get_career_stats(db, wrestler_id, season_id)
    
    # Season stats
    season_stats = get_season_stats(db, wrestler_id, season_id) if season_id else {
        'season_matches': 0, 'season_wins': 0, 'season_win_rate': 0.0
    }
    
    # Previous season win rate
    prev_year_win_rate = get_previous_season_win_rate(db, wrestler_id, season_id) if season_id else 0.5
    
    # Recent form
    win_rate_3 = calculate_win_rate(matches_3, wrestler_id)
    win_rate_5 = calculate_win_rate(matches_5, wrestler_id)
    win_rate_10 = calculate_win_rate(matches_10, wrestler_id)
    win_rate_15 = calculate_win_rate(matches_15, wrestler_id)
    
    streak = calculate_streak(db, wrestler_id, season_id)
    
    # Bonus and close match rates
    bonus_rate_5 = calculate_bonus_win_rate(db, matches_5, wrestler_id)
    bonus_rate_10 = calculate_bonus_win_rate(db, matches_10, wrestler_id)
    close_rate_5 = calculate_close_match_win_rate(matches_5, wrestler_id)
    close_rate_10 = calculate_close_match_win_rate(matches_10, wrestler_id)
    
    # Scoring stats
    avg_scored_3 = calculate_avg_points_scored(matches_3, wrestler_id)
    avg_allowed_3 = calculate_avg_points_allowed(matches_3, wrestler_id)
    avg_scored_5 = calculate_avg_points_scored(matches_5, wrestler_id)
    avg_allowed_5 = calculate_avg_points_allowed(matches_5, wrestler_id)
    avg_scored_10 = calculate_avg_points_scored(matches_10, wrestler_id)
    avg_allowed_10 = calculate_avg_points_allowed(matches_10, wrestler_id)
    
    # Match characteristics
    overtime_rate_5 = calculate_overtime_rate(db, matches_5)
    overtime_rate_10 = calculate_overtime_rate(db, matches_10)
    avg_duration_5 = calculate_avg_duration(db, matches_5)
    avg_duration_10 = calculate_avg_duration(db, matches_10)
    
    # Competition format stats
    dual_tournament_stats = get_dual_tournament_stats(db, wrestler_id, season_id)
    
    # Weight class stats
    wc_stats = get_weight_class_stats(db, wrestler_id, weight_class_id, season_id) if weight_class_id else {
        'weight_class_matches': 0, 'weight_class_wins': 0, 'weight_class_win_rate': 0.5
    }
    
    # Activity metrics
    days_since = calculate_days_since_last_match(db, wrestler_id, reference_date)
    matches_per_week = calculate_matches_per_week(db, wrestler_id, reference_date)
    
    return {
        # Career & season stats
        'career_wins': career_stats['career_wins'],
        'career_losses': career_stats['career_losses'],
        'career_matches': career_stats['career_matches'],
        'season_wins': season_stats['season_wins'],
        'season_matches': season_stats['season_matches'],
        'season_win_rate': season_stats['season_win_rate'],
        'prev_yearly_win_rate': prev_year_win_rate,
        'experience': career_stats['career_matches'],
        
        # Recent form
        'win_rate_last_3': win_rate_3,
        'win_rate_last_5': win_rate_5,
        'win_rate_last_10': win_rate_10,
        'win_rate_last_15': win_rate_15,
        'streak': streak,
        'bonus_win_rate_last_5': bonus_rate_5,
        'bonus_win_rate_last_10': bonus_rate_10,
        'close_match_win_rate_last_5': close_rate_5,
        'close_match_win_rate_last_10': close_rate_10,
        
        # Style / points
        'avg_points_scored_last_3': avg_scored_3,
        'avg_points_allowed_last_3': avg_allowed_3,
        'avg_point_differential_last_3': avg_scored_3 - avg_allowed_3,
        'avg_points_scored_last_5': avg_scored_5,
        'avg_points_allowed_last_5': avg_allowed_5,
        'avg_point_differential_last_5': avg_scored_5 - avg_allowed_5,
        'avg_points_scored_last_10': avg_scored_10,
        'avg_points_allowed_last_10': avg_allowed_10,
        'avg_point_differential_last_10': avg_scored_10 - avg_allowed_10,
        'overtime_rate_last_5': overtime_rate_5,
        'overtime_rate_last_10': overtime_rate_10,
        'avg_duration_last_5': avg_duration_5,
        'avg_duration_last_10': avg_duration_10,
        
        # Dual/tournament/weight-class
        'dual_meet_wins': dual_tournament_stats['dual_meet_wins'],
        'dual_meet_matches': dual_tournament_stats['dual_meet_matches'],
        'dual_meet_win_rate': dual_tournament_stats['dual_meet_win_rate'],
        'tournament_wins': dual_tournament_stats['tournament_wins'],
        'tournament_matches': dual_tournament_stats['tournament_matches'],
        'tournament_win_rate': dual_tournament_stats['tournament_win_rate'],
        'weight_class_matches': wc_stats['weight_class_matches'],
        'weight_class_wins': wc_stats['weight_class_wins'],
        'weight_class_win_rate': wc_stats['weight_class_win_rate'],
        
        # Activity
        'days_since_last_match': days_since,
        'matches_per_week_last_30_days': matches_per_week,
        'year': reference_date.year
    }

def compute_features_for_prediction(
    db: Session, 
    wrestler1_id: int, 
    wrestler2_id: int,
    season_id: Optional[int] = None,
    weight_class_id: Optional[int] = None
) -> Dict:
    """
    Compute all features needed for prediction between two wrestlers
    """
    
    # Compute features for both wrestlers
    w1_features = compute_wrestler_features(db, wrestler1_id, season_id, weight_class_id)
    w2_features = compute_wrestler_features(db, wrestler2_id, season_id, weight_class_id)
    
    # Get head-to-head stats
    h2h_total, h2h_w1_wins, h2h_w2_wins = get_h2h_stats(db, wrestler1_id, wrestler2_id)
    h2h_win_rate = h2h_w1_wins / h2h_total if h2h_total > 0 else 0.5
    
    # Compile all features
    features = {
        # Wrestler 1 features
        **{f'w1_{k}': v for k, v in w1_features.items()},
        
        # Wrestler 2 features
        **{f'w2_{k}': v for k, v in w2_features.items()},
        
        # Head-to-head
        'h2h_matches': h2h_total,
        'h2h_win_rate': h2h_win_rate,
        
        # Differentials (commonly useful for ML models)
        'win_rate_diff_5': w1_features['win_rate_last_5'] - w2_features['win_rate_last_5'],
        'win_rate_diff_10': w1_features['win_rate_last_10'] - w2_features['win_rate_last_10'],
        'point_diff_last_5': w1_features['avg_point_differential_last_5'] - w2_features['avg_point_differential_last_5'],
        'experience_diff': w1_features['experience'] - w2_features['experience'],
        'rest_diff': w1_features['days_since_last_match'] - w2_features['days_since_last_match'],
    }
    
    return features