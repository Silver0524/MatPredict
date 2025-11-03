from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional, List

# Wrestler Schemas
class WrestlerBase(BaseModel):
    name: str
    dob: Optional[date] = None
    hometown: Optional[str] = None
    high_school: Optional[str] = None

class WrestlerCreate(WrestlerBase):
    pass

class Wrestler(WrestlerBase):
    id: int
    
    class Config:
        from_attributes = True

class WrestlerWithStats(Wrestler):
    career_matches: int
    career_wins: int
    career_losses: int
    season_win_rate: Optional[float] = None

# Season Schemas
class SeasonBase(BaseModel):
    start_year: int
    end_year: int
    start_date: Optional[date] = None
    end_date: Optional[date] = None

class SeasonCreate(SeasonBase):
    pass

class Season(SeasonBase):
    id: int
    
    class Config:
        from_attributes = True

# School Schema
class SchoolBase(BaseModel):
    name: str
    conference: Optional[str] = None
    is_active: bool = True

class SchoolCreate(SchoolBase):
    pass

class School(SchoolBase):
    id: int
    
    class Config:
        from_attributes = True

# Weight Class Schemas
class WeightClassBase(BaseModel):
    code: str
    description: Optional[str] = None
    min_weight: Optional[float] = None
    max_weight: Optional[float] = None

class WeightClassCreate(WeightClassBase):
    pass

class WeightClass(WeightClassBase):
    id: int
    
    class Config:
        from_attributes = True

# Result Type Schemas
class ResultTypeBase(BaseModel):
    code: str
    description: Optional[str] = None

class ResultTypeCreate(ResultTypeBase):
    pass

class ResultType(ResultTypeBase):
    id: int
    
    class Config:
        from_attributes = True

# Roster Schemas
class RosterBase(BaseModel):
    school_id: int
    season_id: int

class RosterCreate(RosterBase):
    pass

class Roster(RosterBase):
    id: int
    
    class Config:
        from_attributes = True

class RosterWrestlerBase(BaseModel):
    roster_id: int
    wrestler_id: int

class RosterWrestlerCreate(RosterWrestlerBase):
    pass

class RosterWrestler(RosterWrestlerBase):
    id: int
    
    class Config:
        from_attributes = True

# Meet Schemas
class MeetBase(BaseModel):
    school1_id: int
    school2_id: int
    school1_score: Optional[int] = None
    school2_score: Optional[int] = None
    winner_id: int

class MeetCreate(MeetBase):
    pass

class Meet(MeetBase):
    id: int
    
    class Config:
        from_attributes = True

class MeetWithSchools(Meet):
    school1: School
    school2: School
    winner: School

# Match Schemas
class MatchBase(BaseModel):
    season_id: int
    date: date
    weight_class_id: int
    wrestler1_score: Optional[int] = None
    wrestler2_score: Optional[int] = None
    result_type_id: int

class MatchCreate(MatchBase):
    meet_id: Optional[int] = None
    wrestler1_id: int
    wrestler2_id: int
    winner_id: int

class Match(MatchBase):
    id: int
    meet_id: Optional[int] = None
    wrestler1_id: int
    wrestler2_id: int
    winner_id: int
    
    class Config:
        from_attributes = True

class MatchWithDetails(Match):
    wrestler1: Wrestler
    wrestler2: Wrestler
    winner: Wrestler
    weight_class: WeightClass
    result_type: ResultType

class MatchStats(BaseModel):
    id: int
    match_id: int
    duration_seconds: Optional[int] = None
    
    class Config:
        from_attributes = True

# Wrestler Features Schemas
class WrestlerFeaturesBase(BaseModel):
    wrestler_id: int
    season_id: int
    
    # Career & season stats
    career_wins: int = 0
    career_losses: int = 0
    career_matches: int = 0
    season_wins: int = 0
    season_matches: int = 0
    season_win_rate: Optional[float] = None
    prev_yearly_win_rate: Optional[float] = None
    experience: Optional[int] = None
    
    # Recent form
    win_rate_last_3: Optional[float] = None
    win_rate_last_5: Optional[float] = None
    win_rate_last_10: Optional[float] = None
    win_rate_last_15: Optional[float] = None
    streak: Optional[int] = None
    bonus_win_rate_last_5: Optional[float] = None
    bonus_win_rate_last_10: Optional[float] = None
    close_match_win_rate_last_5: Optional[float] = None
    close_match_win_rate_last_10: Optional[float] = None
    
    # Style / points
    avg_points_scored_last_3: Optional[float] = None
    avg_points_allowed_last_3: Optional[float] = None
    avg_point_differential_last_3: Optional[float] = None
    avg_points_scored_last_5: Optional[float] = None
    avg_points_allowed_last_5: Optional[float] = None
    avg_point_differential_last_5: Optional[float] = None
    avg_points_scored_last_10: Optional[float] = None
    avg_points_allowed_last_10: Optional[float] = None
    avg_point_differential_last_10: Optional[float] = None
    overtime_rate_last_5: Optional[float] = None
    overtime_rate_last_10: Optional[float] = None
    avg_duration_last_5: Optional[float] = None
    avg_duration_last_10: Optional[float] = None
    
    # Dual/tournament/weight-class
    dual_meet_wins: int = 0
    dual_meet_matches: int = 0
    dual_meet_win_rate: Optional[float] = None
    tournament_wins: int = 0
    tournament_matches: int = 0
    tournament_win_rate: Optional[float] = None
    weight_class_matches: int = 0
    weight_class_wins: int = 0
    weight_class_win_rate: Optional[float] = None
    
    # Activity
    days_since_last_match: Optional[int] = None
    matches_per_week_last_30_days: Optional[float] = None
    year: Optional[int] = None

class WrestlerFeaturesCreate(WrestlerFeaturesBase):
    pass

class WrestlerFeatures(WrestlerFeaturesBase):
    id: int
    
    class Config:
        from_attributes = True

# H2H Stats Schemas
class H2HStatsBase(BaseModel):
    wrestler1_id: int
    wrestler2_id: int
    total_matches: int = 0
    wins_wrestler1: int = 0
    wins_wrestler2: int = 0

class H2HStatsCreate(H2HStatsBase):
    pass

class H2HStats(H2HStatsBase):
    id: int
    last_updated: datetime
    
    class Config:
        from_attributes = True

# Prediction Schemas
class PredictionRequest(BaseModel):
    wrestler1_id: int
    wrestler2_id: int
    season_id: Optional[int] = None
    weight_class_id: Optional[int] = None

class PredictionResponse(BaseModel):
    wrestler1_id: int
    wrestler2_id: int
    wrestler1_name: str
    wrestler2_name: str
    wrestler1_win_probability: float
    wrestler2_win_probability: float
    predicted_winner_id: int
    confidence: float
    h2h_stats: Optional[H2HStats] = None
    features: dict

# Feature Update Schema
class FeatureUpdate(BaseModel):
    id: int
    wrestler_id: int
    season_id: int
    last_updated: datetime
    
    class Config:
        from_attributes = True