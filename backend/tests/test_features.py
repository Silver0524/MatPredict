import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from app.ml.features import (
    calculate_win_rate, 
    calculate_avg_point_diff,
    calculate_avg_points_scored,
    calculate_avg_points_allowed,
    calculate_close_match_win_rate
)

def test_win_rate_calculation():
    """Test win rate calculation for both wrestlers"""
    # Mock matches with updated schema (wrestler1_id, wrestler2_id, winner_id)
    class MockMatch:
        def __init__(self, wrestler1_id, wrestler2_id, winner_id):
            self.wrestler1_id = wrestler1_id
            self.wrestler2_id = wrestler2_id
            self.winner_id = winner_id
    
    matches = [
        MockMatch(1, 2, 1),  # Wrestler 1 wins
        MockMatch(1, 3, 1),  # Wrestler 1 wins
        MockMatch(2, 1, 2),  # Wrestler 2 wins (wrestler 1 loses)
        MockMatch(1, 4, 1),  # Wrestler 1 wins
    ]
    
    # Wrestler 1 should have 75% win rate (3 wins out of 4 matches)
    win_rate = calculate_win_rate(matches, wrestler_id=1)
    assert win_rate == 0.75, f"Expected 0.75, got {win_rate}"
    
    # Wrestler 2 should have 100% win rate (1 win out of 1 match where they participated)
    matches_w2 = [m for m in matches if m.wrestler1_id == 2 or m.wrestler2_id == 2]
    win_rate = calculate_win_rate(matches_w2, wrestler_id=2)
    assert win_rate == 0.5, f"Expected 0.5, got {win_rate}"
    
    print("✓ Win rate calculation test passed")

def test_empty_matches():
    """Test handling of empty match lists"""
    win_rate = calculate_win_rate([], wrestler_id=1)
    assert win_rate == 0.0, f"Expected 0.0, got {win_rate}"
    
    point_diff = calculate_avg_point_diff([], wrestler_id=1)
    assert point_diff == 0.0, f"Expected 0.0, got {point_diff}"
    
    print("✓ Empty matches test passed")

def test_point_differential():
    """Test average point differential calculation"""
    class MockMatch:
        def __init__(self, wrestler1_id, wrestler2_id, wrestler1_score, wrestler2_score):
            self.wrestler1_id = wrestler1_id
            self.wrestler2_id = wrestler2_id
            self.wrestler1_score = wrestler1_score
            self.wrestler2_score = wrestler2_score
    
    matches = [
        MockMatch(1, 2, 10, 5),   # +5 for wrestler 1
        MockMatch(1, 3, 8, 6),    # +2 for wrestler 1
        MockMatch(2, 1, 7, 10),   # +3 for wrestler 1 (they're wrestler2 here)
        MockMatch(1, 4, 6, 9),    # -3 for wrestler 1
    ]
    
    avg_diff = calculate_avg_point_diff(matches, wrestler_id=1)
    expected = (5 + 2 + 3 - 3) / 4  # = 1.75
    assert avg_diff == expected, f"Expected {expected}, got {avg_diff}"
    
    print("✓ Point differential test passed")

def test_points_scored_allowed():
    """Test average points scored and allowed calculation"""
    class MockMatch:
        def __init__(self, wrestler1_id, wrestler2_id, wrestler1_score, wrestler2_score):
            self.wrestler1_id = wrestler1_id
            self.wrestler2_id = wrestler2_id
            self.wrestler1_score = wrestler1_score
            self.wrestler2_score = wrestler2_score
    
    matches = [
        MockMatch(1, 2, 10, 5),   # Wrestler 1 scored 10, allowed 5
        MockMatch(1, 3, 8, 6),    # Wrestler 1 scored 8, allowed 6
        MockMatch(2, 1, 7, 12),   # Wrestler 1 scored 12, allowed 7
    ]
    
    avg_scored = calculate_avg_points_scored(matches, wrestler_id=1)
    expected_scored = (10 + 8 + 12) / 3  # = 10.0
    assert avg_scored == expected_scored, f"Expected {expected_scored}, got {avg_scored}"
    
    avg_allowed = calculate_avg_points_allowed(matches, wrestler_id=1)
    expected_allowed = (5 + 6 + 7) / 3  # = 6.0
    assert avg_allowed == expected_allowed, f"Expected {expected_allowed}, got {avg_allowed}"
    
    print("✓ Points scored/allowed test passed")

def test_close_match_win_rate():
    """Test close match (within 3 points) win rate calculation"""
    class MockMatch:
        def __init__(self, wrestler1_id, wrestler2_id, winner_id, wrestler1_score, wrestler2_score):
            self.wrestler1_id = wrestler1_id
            self.wrestler2_id = wrestler2_id
            self.winner_id = winner_id
            self.wrestler1_score = wrestler1_score
            self.wrestler2_score = wrestler2_score
    
    matches = [
        MockMatch(1, 2, 1, 10, 8),   # Close match, wrestler 1 wins (2 point diff)
        MockMatch(1, 3, 3, 5, 8),    # Close match, wrestler 1 loses (3 point diff)
        MockMatch(1, 4, 1, 15, 5),   # Not close (10 point diff)
        MockMatch(1, 5, 1, 7, 6),    # Close match, wrestler 1 wins (1 point diff)
    ]
    
    close_win_rate = calculate_close_match_win_rate(matches, wrestler_id=1)
    # 3 close matches, 2 wins = 2/3 ≈ 0.667
    expected = 2 / 3
    assert abs(close_win_rate - expected) < 0.01, f"Expected {expected}, got {close_win_rate}"
    
    print("✓ Close match win rate test passed")

def test_matches_with_none_scores():
    """Test handling of matches with None scores (e.g., forfeits)"""
    class MockMatch:
        def __init__(self, wrestler1_id, wrestler2_id, wrestler1_score, wrestler2_score):
            self.wrestler1_id = wrestler1_id
            self.wrestler2_id = wrestler2_id
            self.wrestler1_score = wrestler1_score
            self.wrestler2_score = wrestler2_score
    
    matches = [
        MockMatch(1, 2, 10, 5),
        MockMatch(1, 3, None, None),  # Forfeit/no score
        MockMatch(1, 4, 8, 6),
    ]
    
    # Should only count matches with valid scores
    avg_diff = calculate_avg_point_diff(matches, wrestler_id=1)
    expected = (5 + 2) / 2  # = 3.5
    assert avg_diff == expected, f"Expected {expected}, got {avg_diff}"
    
    avg_scored = calculate_avg_points_scored(matches, wrestler_id=1)
    expected_scored = (10 + 8) / 2  # = 9.0
    assert avg_scored == expected_scored, f"Expected {expected_scored}, got {avg_scored}"
    
    print("✓ None scores handling test passed")

if __name__ == "__main__":
    print("Running feature calculation tests...\n")
    
    test_win_rate_calculation()
    test_empty_matches()
    test_point_differential()
    test_points_scored_allowed()
    test_close_match_win_rate()
    test_matches_with_none_scores()
    
    print("\n✅ All tests passed!")