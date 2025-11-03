from sqlalchemy.orm import Session
from sqlalchemy import desc, or_, and_
from app import models, schemas
from typing import List, Optional
from datetime import date

# Wrestler CRUD
def get_wrestlers(db: Session, skip: int = 0, limit: int = 100) -> List[models.Wrestler]:
    return db.query(models.Wrestler).offset(skip).limit(limit).all()

def get_wrestler(db: Session, wrestler_id: int) -> Optional[models.Wrestler]:
    return db.query(models.Wrestler).filter(models.Wrestler.id == wrestler_id).first()

def create_wrestler(db: Session, wrestler: schemas.WrestlerCreate) -> models.Wrestler:
    db_wrestler = models.Wrestler(**wrestler.model_dump())
    db.add(db_wrestler)
    db.commit()
    db.refresh(db_wrestler)
    return db_wrestler

def search_wrestlers(db: Session, query: str) -> List[models.Wrestler]:
    search = f"%{query}%"
    return db.query(models.Wrestler).filter(
        models.Wrestler.name.ilike(search)
    ).limit(50).all()

# Match CRUD
def get_wrestler_matches(
    db: Session, 
    wrestler_id: int, 
    season_id: Optional[int] = None,
    limit: int = 20
) -> List[models.Match]:
    query = db.query(models.Match).filter(
        or_(
            models.Match.wrestler1_id == wrestler_id,
            models.Match.wrestler2_id == wrestler_id
        )
    )
    
    if season_id:
        query = query.filter(models.Match.season_id == season_id)
    
    return query.order_by(desc(models.Match.date)).limit(limit).all()

def get_match(db: Session, match_id: int) -> Optional[models.Match]:
    return db.query(models.Match).filter(models.Match.id == match_id).first()

def create_match(db: Session, match: schemas.MatchCreate) -> models.Match:
    db_match = models.Match(**match.model_dump())
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match

def get_matches_by_date_range(
    db: Session,
    start_date: date,
    end_date: date,
    season_id: Optional[int] = None
) -> List[models.Match]:
    query = db.query(models.Match).filter(
        and_(
            models.Match.date >= start_date,
            models.Match.date <= end_date
        )
    )
    
    if season_id:
        query = query.filter(models.Match.season_id == season_id)
    
    return query.order_by(models.Match.date).all()

# Wrestler Features CRUD
def get_wrestler_features(
    db: Session, 
    wrestler_id: int,
    season_id: Optional[int] = None
) -> Optional[models.WrestlerFeatures]:
    query = db.query(models.WrestlerFeatures).filter(
        models.WrestlerFeatures.wrestler_id == wrestler_id
    )
    
    if season_id:
        query = query.filter(models.WrestlerFeatures.season_id == season_id)
    
    return query.first()

def get_all_wrestler_features(
    db: Session,
    season_id: Optional[int] = None
) -> List[models.WrestlerFeatures]:
    query = db.query(models.WrestlerFeatures)
    
    if season_id:
        query = query.filter(models.WrestlerFeatures.season_id == season_id)
    
    return query.all()

def create_wrestler_features(
    db: Session, 
    features: schemas.WrestlerFeaturesCreate
) -> models.WrestlerFeatures:
    db_features = models.WrestlerFeatures(**features.model_dump())
    db.add(db_features)
    db.commit()
    db.refresh(db_features)
    return db_features

def update_wrestler_features(
    db: Session,
    wrestler_id: int,
    season_id: int,
    features: schemas.WrestlerFeaturesBase
) -> Optional[models.WrestlerFeatures]:
    db_features = db.query(models.WrestlerFeatures).filter(
        and_(
            models.WrestlerFeatures.wrestler_id == wrestler_id,
            models.WrestlerFeatures.season_id == season_id
        )
    ).first()
    
    if db_features:
        for key, value in features.model_dump(exclude={'wrestler_id', 'season_id'}).items():
            setattr(db_features, key, value)
        db.commit()
        db.refresh(db_features)
    
    return db_features

# H2H Stats CRUD
def get_h2h_stats(db: Session, wrestler1_id: int, wrestler2_id: int) -> Optional[models.H2HStats]:
    return db.query(models.H2HStats).filter(
        or_(
            and_(
                models.H2HStats.wrestler1_id == wrestler1_id,
                models.H2HStats.wrestler2_id == wrestler2_id
            ),
            and_(
                models.H2HStats.wrestler1_id == wrestler2_id,
                models.H2HStats.wrestler2_id == wrestler1_id
            )
        )
    ).first()

def create_h2h_stats(db: Session, h2h: schemas.H2HStatsCreate) -> models.H2HStats:
    db_h2h = models.H2HStats(**h2h.model_dump())
    db.add(db_h2h)
    db.commit()
    db.refresh(db_h2h)
    return db_h2h

def update_h2h_stats(
    db: Session,
    wrestler1_id: int,
    wrestler2_id: int,
    h2h: schemas.H2HStatsBase
) -> Optional[models.H2HStats]:
    db_h2h = get_h2h_stats(db, wrestler1_id, wrestler2_id)
    
    if db_h2h:
        for key, value in h2h.model_dump(exclude={'wrestler1_id', 'wrestler2_id'}).items():
            setattr(db_h2h, key, value)
        db.commit()
        db.refresh(db_h2h)
    
    return db_h2h

# School CRUD
def get_schools(db: Session, active_only: bool = True) -> List[models.School]:
    query = db.query(models.School)
    
    if active_only:
        query = query.filter(models.School.is_active == True)
    
    return query.order_by(models.School.name).all()

def get_school(db: Session, school_id: int) -> Optional[models.School]:
    return db.query(models.School).filter(models.School.id == school_id).first()

def create_school(db: Session, school: schemas.SchoolCreate) -> models.School:
    db_school = models.School(**school.model_dump())
    db.add(db_school)
    db.commit()
    db.refresh(db_school)
    return db_school

# Season CRUD
def get_seasons(db: Session) -> List[models.Season]:
    return db.query(models.Season).order_by(desc(models.Season.start_year)).all()

def get_season(db: Session, season_id: int) -> Optional[models.Season]:
    return db.query(models.Season).filter(models.Season.id == season_id).first()

def get_current_season(db: Session) -> Optional[models.Season]:
    return db.query(models.Season).order_by(desc(models.Season.start_year)).first()

def create_season(db: Session, season: schemas.SeasonCreate) -> models.Season:
    db_season = models.Season(**season.model_dump())
    db.add(db_season)
    db.commit()
    db.refresh(db_season)
    return db_season

# Weight Class CRUD
def get_weight_classes(db: Session) -> List[models.WeightClass]:
    return db.query(models.WeightClass).order_by(models.WeightClass.code).all()

def get_weight_class(db: Session, weight_class_id: int) -> Optional[models.WeightClass]:
    return db.query(models.WeightClass).filter(models.WeightClass.id == weight_class_id).first()

def get_weight_class_by_code(db: Session, code: str) -> Optional[models.WeightClass]:
    return db.query(models.WeightClass).filter(models.WeightClass.code == code).first()

def create_weight_class(db: Session, weight_class: schemas.WeightClassCreate) -> models.WeightClass:
    db_weight_class = models.WeightClass(**weight_class.model_dump())
    db.add(db_weight_class)
    db.commit()
    db.refresh(db_weight_class)
    return db_weight_class

# Result Type CRUD
def get_result_types(db: Session) -> List[models.ResultType]:
    return db.query(models.ResultType).order_by(models.ResultType.code).all()

def get_result_type(db: Session, result_type_id: int) -> Optional[models.ResultType]:
    return db.query(models.ResultType).filter(models.ResultType.id == result_type_id).first()

def get_result_type_by_code(db: Session, code: str) -> Optional[models.ResultType]:
    return db.query(models.ResultType).filter(models.ResultType.code == code).first()

def create_result_type(db: Session, result_type: schemas.ResultTypeCreate) -> models.ResultType:
    db_result_type = models.ResultType(**result_type.model_dump())
    db.add(db_result_type)
    db.commit()
    db.refresh(db_result_type)
    return db_result_type

# Roster CRUD
def get_roster(db: Session, school_id: int, season_id: int) -> Optional[models.Roster]:
    return db.query(models.Roster).filter(
        and_(
            models.Roster.school_id == school_id,
            models.Roster.season_id == season_id
        )
    ).first()

def get_roster_wrestlers(db: Session, roster_id: int) -> List[models.RosterWrestler]:
    return db.query(models.RosterWrestler).filter(
        models.RosterWrestler.roster_id == roster_id
    ).all()

def create_roster(db: Session, roster: schemas.RosterCreate) -> models.Roster:
    db_roster = models.Roster(**roster.model_dump())
    db.add(db_roster)
    db.commit()
    db.refresh(db_roster)
    return db_roster

def add_wrestler_to_roster(
    db: Session, 
    roster_wrestler: schemas.RosterWrestlerCreate
) -> models.RosterWrestler:
    db_roster_wrestler = models.RosterWrestler(**roster_wrestler.model_dump())
    db.add(db_roster_wrestler)
    db.commit()
    db.refresh(db_roster_wrestler)
    return db_roster_wrestler

# Meet CRUD
def get_meet(db: Session, meet_id: int) -> Optional[models.Meet]:
    return db.query(models.Meet).filter(models.Meet.id == meet_id).first()

def get_school_meets(db: Session, school_id: int, season_id: Optional[int] = None) -> List[models.Meet]:
    query = db.query(models.Meet).filter(
        or_(
            models.Meet.school1_id == school_id,
            models.Meet.school2_id == school_id
        )
    )
    
    # Note: Need to join with matches to filter by season since meets don't have season_id
    if season_id:
        query = query.join(models.Match).filter(models.Match.season_id == season_id)
    
    return query.all()

def create_meet(db: Session, meet: schemas.MeetCreate) -> models.Meet:
    db_meet = models.Meet(**meet.model_dump())
    db.add(db_meet)
    db.commit()
    db.refresh(db_meet)
    return db_meet

# Match Stats CRUD
def get_match_stats(db: Session, match_id: int) -> Optional[models.MatchStats]:
    return db.query(models.MatchStats).filter(models.MatchStats.match_id == match_id).first()

def create_match_stats(db: Session, match_id: int, duration_seconds: Optional[int] = None) -> models.MatchStats:
    db_stats = models.MatchStats(match_id=match_id, duration_seconds=duration_seconds)
    db.add(db_stats)
    db.commit()
    db.refresh(db_stats)
    return db_stats