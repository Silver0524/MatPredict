from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey, DateTime, Boolean, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class School(Base):
    __tablename__ = "schools"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    conference = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    
    rosters = relationship("Roster", back_populates="school")
    meets_as_school1 = relationship("Meet", foreign_keys="Meet.school1_id", back_populates="school1")
    meets_as_school2 = relationship("Meet", foreign_keys="Meet.school2_id", back_populates="school2")
    meet_wins = relationship("Meet", foreign_keys="Meet.winner_id", back_populates="winner")

class Season(Base):
    __tablename__ = "seasons"
    
    id = Column(Integer, primary_key=True, index=True)
    start_year = Column(Integer, nullable=False)
    end_year = Column(Integer, nullable=False)
    start_date = Column(Date, nullable=True)
    end_date = Column(Date, nullable=True)
    
    rosters = relationship("Roster", back_populates="season")
    matches = relationship("Match", back_populates="season")
    wrestler_features = relationship("WrestlerFeatures", back_populates="season")
    feature_updates = relationship("FeatureUpdate", back_populates="season")

class Wrestler(Base):
    __tablename__ = "wrestlers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    dob = Column(Date, nullable=True)
    hometown = Column(String, nullable=True)
    high_school = Column(String, nullable=True)
    
    roster_wrestlers = relationship("RosterWrestler", back_populates="wrestler")
    matches_as_wrestler1 = relationship("Match", foreign_keys="Match.wrestler1_id", back_populates="wrestler1")
    matches_as_wrestler2 = relationship("Match", foreign_keys="Match.wrestler2_id", back_populates="wrestler2")
    match_wins = relationship("Match", foreign_keys="Match.winner_id", back_populates="winner")
    features = relationship("WrestlerFeatures", back_populates="wrestler")
    feature_updates = relationship("FeatureUpdate", back_populates="wrestler")
    h2h_as_wrestler1 = relationship("H2HStats", foreign_keys="H2HStats.wrestler1_id", back_populates="wrestler1")
    h2h_as_wrestler2 = relationship("H2HStats", foreign_keys="H2HStats.wrestler2_id", back_populates="wrestler2")

class Roster(Base):
    __tablename__ = "rosters"
    
    id = Column(Integer, primary_key=True, index=True)
    school_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    season_id = Column(Integer, ForeignKey("seasons.id"), nullable=False)
    
    school = relationship("School", back_populates="rosters")
    season = relationship("Season", back_populates="rosters")
    roster_wrestlers = relationship("RosterWrestler", back_populates="roster")

class RosterWrestler(Base):
    __tablename__ = "roster_wrestlers"
    
    id = Column(Integer, primary_key=True, index=True)
    roster_id = Column(Integer, ForeignKey("rosters.id"), nullable=False)
    wrestler_id = Column(Integer, ForeignKey("wrestlers.id"), nullable=False)
    
    roster = relationship("Roster", back_populates="roster_wrestlers")
    wrestler = relationship("Wrestler", back_populates="roster_wrestlers")

class Meet(Base):
    __tablename__ = "meets"
    
    id = Column(Integer, primary_key=True, index=True)
    school1_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    school2_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    school1_score = Column(Integer, nullable=True)
    school2_score = Column(Integer, nullable=True)
    winner_id = Column(Integer, ForeignKey("schools.id"), nullable=False)
    
    school1 = relationship("School", foreign_keys=[school1_id], back_populates="meets_as_school1")
    school2 = relationship("School", foreign_keys=[school2_id], back_populates="meets_as_school2")
    winner = relationship("School", foreign_keys=[winner_id], back_populates="meet_wins")
    matches = relationship("Match", back_populates="meet")

class ResultType(Base):
    __tablename__ = "result_types"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, nullable=False, unique=True)  # e.g., "DEC", "MD", "TF", "PIN"
    description = Column(String, nullable=True)  # e.g., "Decision", "Major Decision"
    
    matches = relationship("Match", back_populates="result_type")

class WeightClass(Base):
    __tablename__ = "weight_classes"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, nullable=False, unique=True)  # e.g., "125", "133", "285"
    description = Column(String, nullable=True)  # e.g., "125 lbs", "Heavyweight"
    min_weight = Column(Numeric, nullable=True)
    max_weight = Column(Numeric, nullable=True)
    
    matches = relationship("Match", back_populates="weight_class")

class Match(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    meet_id = Column(Integer, ForeignKey("meets.id"), nullable=True)  # nullable for tournament matches
    season_id = Column(Integer, ForeignKey("seasons.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    weight_class_id = Column(Integer, ForeignKey("weight_classes.id"), nullable=False)
    wrestler1_id = Column(Integer, ForeignKey("wrestlers.id"), nullable=False)
    wrestler2_id = Column(Integer, ForeignKey("wrestlers.id"), nullable=False)
    wrestler1_score = Column(Integer, nullable=True)
    wrestler2_score = Column(Integer, nullable=True)
    winner_id = Column(Integer, ForeignKey("wrestlers.id"), nullable=False)
    result_type_id = Column(Integer, ForeignKey("result_types.id"), nullable=False)
    
    meet = relationship("Meet", back_populates="matches")
    season = relationship("Season", back_populates="matches")
    weight_class = relationship("WeightClass", back_populates="matches")
    wrestler1 = relationship("Wrestler", foreign_keys=[wrestler1_id], back_populates="matches_as_wrestler1")
    wrestler2 = relationship("Wrestler", foreign_keys=[wrestler2_id], back_populates="matches_as_wrestler2")
    winner = relationship("Wrestler", foreign_keys=[winner_id], back_populates="match_wins")
    result_type = relationship("ResultType", back_populates="matches")
    stats = relationship("MatchStats", back_populates="match", uselist=False)

class MatchStats(Base):
    __tablename__ = "match_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, unique=True)
    duration_seconds = Column(Integer, nullable=True)
    # Add other stats as needed
    
    match = relationship("Match", back_populates="stats")

class WrestlerFeatures(Base):
    __tablename__ = "wrestler_features"
    
    id = Column(Integer, primary_key=True, index=True)
    wrestler_id = Column(Integer, ForeignKey("wrestlers.id"), nullable=False)
    season_id = Column(Integer, ForeignKey("seasons.id"), nullable=False)
    
    # Career & season stats
    career_wins = Column(Integer, default=0)
    career_losses = Column(Integer, default=0)
    career_matches = Column(Integer, default=0)
    season_wins = Column(Integer, default=0)
    season_matches = Column(Integer, default=0)
    season_win_rate = Column(Numeric, nullable=True)
    prev_yearly_win_rate = Column(Numeric, nullable=True)
    experience = Column(Integer, nullable=True)
    
    # Recent form
    win_rate_last_3 = Column(Numeric, nullable=True)
    win_rate_last_5 = Column(Numeric, nullable=True)
    win_rate_last_10 = Column(Numeric, nullable=True)
    win_rate_last_15 = Column(Numeric, nullable=True)
    streak = Column(Integer, nullable=True)
    bonus_win_rate_last_5 = Column(Numeric, nullable=True)
    bonus_win_rate_last_10 = Column(Numeric, nullable=True)
    close_match_win_rate_last_5 = Column(Numeric, nullable=True)
    close_match_win_rate_last_10 = Column(Numeric, nullable=True)
    
    # Style / points
    avg_points_scored_last_3 = Column(Numeric, nullable=True)
    avg_points_allowed_last_3 = Column(Numeric, nullable=True)
    avg_point_differential_last_3 = Column(Numeric, nullable=True)
    avg_points_scored_last_5 = Column(Numeric, nullable=True)
    avg_points_allowed_last_5 = Column(Numeric, nullable=True)
    avg_point_differential_last_5 = Column(Numeric, nullable=True)
    avg_points_scored_last_10 = Column(Numeric, nullable=True)
    avg_points_allowed_last_10 = Column(Numeric, nullable=True)
    avg_point_differential_last_10 = Column(Numeric, nullable=True)
    overtime_rate_last_5 = Column(Numeric, nullable=True)
    overtime_rate_last_10 = Column(Numeric, nullable=True)
    avg_duration_last_5 = Column(Numeric, nullable=True)
    avg_duration_last_10 = Column(Numeric, nullable=True)
    
    # Dual/tournament/weight-class
    dual_meet_wins = Column(Integer, default=0)
    dual_meet_matches = Column(Integer, default=0)
    dual_meet_win_rate = Column(Numeric, nullable=True)
    tournament_wins = Column(Integer, default=0)
    tournament_matches = Column(Integer, default=0)
    tournament_win_rate = Column(Numeric, nullable=True)
    weight_class_matches = Column(Integer, default=0)
    weight_class_wins = Column(Integer, default=0)
    weight_class_win_rate = Column(Numeric, nullable=True)
    
    # Activity
    days_since_last_match = Column(Integer, nullable=True)
    matches_per_week_last_30_days = Column(Numeric, nullable=True)
    year = Column(Integer, nullable=True)
    
    wrestler = relationship("Wrestler", back_populates="features")
    season = relationship("Season", back_populates="wrestler_features")

class FeatureUpdate(Base):
    __tablename__ = "feature_updates"
    
    id = Column(Integer, primary_key=True, index=True)
    wrestler_id = Column(Integer, ForeignKey("wrestlers.id"), nullable=False)
    season_id = Column(Integer, ForeignKey("seasons.id"), nullable=False)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    
    wrestler = relationship("Wrestler", back_populates="feature_updates")
    season = relationship("Season", back_populates="feature_updates")

class H2HStats(Base):
    __tablename__ = "h2h_stats"
    
    id = Column(Integer, primary_key=True, index=True)
    wrestler1_id = Column(Integer, ForeignKey("wrestlers.id"), nullable=False)
    wrestler2_id = Column(Integer, ForeignKey("wrestlers.id"), nullable=False)
    total_matches = Column(Integer, default=0)
    wins_wrestler1 = Column(Integer, default=0)
    wins_wrestler2 = Column(Integer, default=0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now())
    
    wrestler1 = relationship("Wrestler", foreign_keys=[wrestler1_id], back_populates="h2h_as_wrestler1")
    wrestler2 = relationship("Wrestler", foreign_keys=[wrestler2_id], back_populates="h2h_as_wrestler2")