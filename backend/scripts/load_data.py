import pandas as pd
import sys
from pathlib import Path
from sqlalchemy.orm import Session
from datetime import datetime

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from app.database import SessionLocal, engine
from app.models import (
    School, Wrestler, Season, Roster, RosterWrestler, Meet, Match, 
    WrestlerFeatures, ResultType, WeightClass, MatchStats
)

def load_csv_data(csv_path: str):
    """Load wrestling data from CSV into database"""
    
    print(f"Loading data from {csv_path}...")
    df = pd.read_csv(csv_path)
    
    print(f"Loaded {len(df)} rows")
    print(f"Columns: {df.columns.tolist()}")
    
    db = SessionLocal()
    
    try:
        # Create seasons
        print("\nCreating seasons...")
        seasons = {}
        for season_str in df['season'].unique():
            # Parse season like "2013/2014"
            start_year, end_year = season_str.split('/')
            season_key = season_str
            
            season = Season(
                start_year=int(start_year),
                end_year=int(end_year)
            )
            db.add(season)
            db.flush()
            seasons[season_key] = season
            print(f"  - Season {season_str}")
        
        db.commit()
        
        # Create weight classes
        print("\nCreating weight classes...")
        weight_classes = {}
        for wc in df['weight_class'].unique():
            if pd.notna(wc):
                wc_str = str(int(wc))
                weight_class = WeightClass(
                    code=wc_str,
                    description=f"{wc_str} lbs"
                )
                db.add(weight_class)
                db.flush()
                weight_classes[wc_str] = weight_class
                print(f"  - {wc_str} lbs")
        
        db.commit()
        
        # Create result types
        print("\nCreating result types...")
        result_types = {}
        result_type_descriptions = {
            'DEC': 'Decision',
            'MD': 'Major Decision',
            'TF': 'Technical Fall',
            'PIN': 'Pin/Fall',
            'FF': 'Forfeit',
            'DQ': 'Disqualification',
            'INJ': 'Injury Default'
        }
        
        for rt in df['result_type'].unique():
            if pd.notna(rt):
                rt_str = str(rt).upper()
                result_type = ResultType(
                    code=rt_str,
                    description=result_type_descriptions.get(rt_str, rt_str)
                )
                db.add(result_type)
                db.flush()
                result_types[rt_str] = result_type
                print(f"  - {rt_str}: {result_type.description}")
        
        db.commit()

        # Known inactive schools
        inactive_schools = ["Boston U", "Boise State", "Eastern Michigan", 
                            "Old Dominion", "Fresno State"]

        # Determine active schools based on 2024/2025 season participation
        active_schools = []
        for school in pd.concat([df['wrestler_school'], df['opponent_school']]).unique():
            if "2024/2025" in df[(df['wrestler_school'] == school)]['season'].unique():
                active_schools.append(school)
            elif "2024/2025" in df[(df['opponent_school'] == school)]['season'].unique():
                active_schools.append(school)

        # Create schools
        print("\nCreating schools...")
        schools = {}
        for school_name in pd.concat([df['wrestler_school'], df['opponent_school']]).unique():
            if pd.notna(school_name):
                # Set is_active based on known inactive list and 2024/2025 participation
                is_active = None
                if school_name in inactive_schools:
                    is_active = False
                elif school_name in active_schools:
                    is_active = True

                if is_active is None:
                    school = School(
                        name=school_name,
                    )
                else:
                    school = School(
                        name=school_name,
                        is_active=is_active
                    )
                db.add(school)
                db.flush()
                schools[school_name] = school
                print(f"  - {school_name}")
        
        db.commit()
        
        # Create wrestlers
        print("\nCreating wrestlers...")
        wrestlers = {}
        
        # Collect unique wrestlers from both wrestler and opponent
        wrestler_data = []
        for _, row in df.iterrows():
            wrestler_data.append({
                'name': row['wrestler'],
                'wrestler_id': row['wrestler_id']
            })
            wrestler_data.append({
                'name': row['opponent'],
                'wrestler_id': row['opponent_id']
            })
        
        # Remove duplicates based on wrestler_id
        wrestler_df = pd.DataFrame(wrestler_data).drop_duplicates(subset=['wrestler_id'])
        
        for _, wrestler_row in wrestler_df.iterrows():
            wrestler = Wrestler(
                name=wrestler_row['name']
            )
            db.add(wrestler)
            db.flush()
            wrestlers[int(wrestler_row['wrestler_id'])] = wrestler
            print(f"  - {wrestler_row['name']} (ID: {wrestler_row['wrestler_id']})")
        
        db.commit()
        
        # Create rosters (link wrestlers to schools for seasons)
        print("\nCreating rosters and roster wrestlers...")
        roster_cache = {}  # (school_id, season_id) -> roster
        roster_wrestler_keys = set()
        
        for _, row in df.iterrows():
            season_id = seasons[row['season']].id
            
            # Handle wrestler's roster
            wrestler_school_id = schools[row['wrestler_school']].id
            roster_key = (wrestler_school_id, season_id)
            
            if roster_key not in roster_cache:
                roster = Roster(
                    school_id=wrestler_school_id,
                    season_id=season_id
                )
                db.add(roster)
                db.flush()
                roster_cache[roster_key] = roster
            
            wrestler_roster_key = (roster_cache[roster_key].id, wrestlers[int(row['wrestler_id'])].id)
            if wrestler_roster_key not in roster_wrestler_keys:
                roster_wrestler = RosterWrestler(
                    roster_id=roster_cache[roster_key].id,
                    wrestler_id=wrestlers[int(row['wrestler_id'])].id
                )
                db.add(roster_wrestler)
                roster_wrestler_keys.add(wrestler_roster_key)
            
            # Handle opponent's roster
            opponent_school_id = schools[row['opponent_school']].id
            roster_key = (opponent_school_id, season_id)
            
            if roster_key not in roster_cache:
                roster = Roster(
                    school_id=opponent_school_id,
                    season_id=season_id
                )
                db.add(roster)
                db.flush()
                roster_cache[roster_key] = roster
            
            opponent_roster_key = (roster_cache[roster_key].id, wrestlers[int(row['opponent_id'])].id)
            if opponent_roster_key not in roster_wrestler_keys:
                roster_wrestler = RosterWrestler(
                    roster_id=roster_cache[roster_key].id,
                    wrestler_id=wrestlers[int(row['opponent_id'])].id
                )
                db.add(roster_wrestler)
                roster_wrestler_keys.add(opponent_roster_key)
        
        db.commit()
        print(f"Created {len(roster_cache)} rosters and {len(roster_wrestler_keys)} roster-wrestler links")
        
        # Create matches (ignoring meets for now)
        print("\nCreating matches...")
        
        for idx, row in df.iterrows():
            # Determine winner
            winner_id = None
            if row['is_win'] == 1:
                winner_id = wrestlers[int(row['wrestler_id'])].id
            else:
                winner_id = wrestlers[int(row['opponent_id'])].id
            
            # Create match
            match = Match(
                meet_id=None,  # Ignoring meets for now
                season_id=seasons[row['season']].id,
                date=datetime.strptime(row['date'], '%Y-%m-%d').date(),
                weight_class_id=weight_classes[str(int(row['weight_class']))].id,
                wrestler1_id=wrestlers[int(row['wrestler_id'])].id,
                wrestler2_id=wrestlers[int(row['opponent_id'])].id,
                wrestler1_score=int(row['wrestler_score']) if pd.notna(row['wrestler_score']) else None,
                wrestler2_score=int(row['opponent_score']) if pd.notna(row['opponent_score']) else None,
                winner_id=winner_id,
                result_type_id=result_types[str(row['result_type']).upper()].id
            )
            db.add(match)
            db.flush()
            
            # Create match stats if duration is available
            if pd.notna(row.get('duration_seconds')):
                match_stats = MatchStats(
                    match_id=match.id,
                    duration_seconds=int(row['duration_seconds'])
                )
                db.add(match_stats)
            
            if (idx + 1) % 100 == 0:
                print(f"  Processed {idx + 1}/{len(df)} matches...")
                db.commit()  # Commit in batches
        
        db.commit()
        
        # Create empty features for each wrestler-season combination
        print("\nCreating wrestler features...")
        for season_key, season in seasons.items():
            for wrestler_id, wrestler in wrestlers.items():
                features = WrestlerFeatures(
                    wrestler_id=wrestler.id,
                    season_id=season.id
                )
                db.add(features)
        
        db.commit()
        
        print(f"\nSuccessfully loaded {len(df)} matches!")
        print(f"  - {len(seasons)} seasons")
        print(f"  - {len(schools)} schools")
        print(f"  - {len(wrestlers)} wrestlers")
        print(f"  - {len(weight_classes)} weight classes")
        print(f"  - {len(result_types)} result types")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise
    finally:
        db.close()

if __name__ == "__main__":
    csv_path = "../../data/d1_results_base_features.csv"
    load_csv_data(csv_path)