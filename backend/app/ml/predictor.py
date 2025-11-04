import pickle
import numpy as np
from pathlib import Path
from typing import Dict, Tuple
import os

class WrestlingPredictor:
    def __init__(self, model_path: str = None):
        """Load the trained model"""
        if model_path is None:
            model_path = os.getenv("MODEL_PATH", "models/decision_tree_model.pkl")
        
        self.model_path = Path(model_path)
        
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found at {self.model_path}")
        
        with open(self.model_path, 'rb') as f:
            self.model = pickle.load(f)
        
        print(f"Model loaded from {self.model_path}")
        
        # IMPORTANT: Define the exact feature order your model expects
        # This must match the order used during training!
        self.feature_names = [
            # Career & season stats
            'career_wins',
            'career_losses',
            'career_matches',
            'season_wins',
            'season_matches',
            'season_win_rate',
            'prev_yearly_win_rate',
            'experience',
            
            # Recent form
            'win_rate_last_3',
            'win_rate_last_5',
            'win_rate_last_10',
            'win_rate_last_15',
            'streak',
            'bonus_win_rate_last_5',
            'bonus_win_rate_last_10',
            'close_match_win_rate_last_5',
            'close_match_win_rate_last_10',
            
            # Style / points
            'avg_points_scored_last_3',
            'avg_points_allowed_last_3',
            'avg_point_differential_last_3',
            'avg_points_scored_last_5',
            'avg_points_allowed_last_5',
            'avg_point_differential_last_5',
            'avg_points_scored_last_10',
            'avg_points_allowed_last_10',
            'avg_point_differential_last_10',
            'overtime_rate_last_5',
            'overtime_rate_last_10',
            'avg_duration_last_5',
            'avg_duration_last_10',
            
            # Dual/tournament/weight-class
            'dual_meet_wins',
            'dual_meet_matches',
            'dual_meet_win_rate',
            'tournament_wins',
            'tournament_matches',
            'tournament_win_rate',
            'weight_class_matches',
            'weight_class_wins',
            'weight_class_win_rate',
            
            # Activity
            'days_since_last_match',
            'matches_per_week_last_30_days',
            'year'
            ]
    
    def prepare_features(self, features: Dict) -> np.ndarray:
        """Convert feature dict to numpy array in correct order"""
        feature_values = []
        
        for feature_name in self.feature_names:
            if feature_name not in features:
                raise ValueError(f"Missing feature: {feature_name}")
            feature_values.append(features[feature_name])
        
        return np.array(feature_values).reshape(1, -1)
    
    def predict(self, features: Dict) -> Tuple[float, float]:
        """
        Make prediction
        
        Returns:
            (wrestler1_win_prob, wrestler2_win_prob)
        """
        X = self.prepare_features(features)
        
        # Get prediction probabilities
        # Most sklearn classifiers have predict_proba method
        if hasattr(self.model, 'predict_proba'):
            proba = self.model.predict_proba(X)[0]
            
            # Assuming binary classification where class 1 = wrestler1 wins
            # Adjust based on your model's training
            wrestler1_prob = proba[1]
            wrestler2_prob = proba[0]
        else:
            # Fallback for models without predict_proba
            prediction = self.model.predict(X)[0]
            wrestler1_prob = float(prediction)
            wrestler2_prob = 1.0 - wrestler1_prob
        
        return wrestler1_prob, wrestler2_prob
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get feature importance if model supports it"""
        if hasattr(self.model, 'feature_importances_'):
            importance = self.model.feature_importances_
            return dict(zip(self.feature_names, importance))
        return {}

# Global predictor instance
predictor = None

def get_predictor() -> WrestlingPredictor:
    """Get or create predictor singleton"""
    global predictor
    if predictor is None:
        predictor = WrestlingPredictor()
    return predictor