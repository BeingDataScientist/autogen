"""
ML Model - Isolation Forest for anomaly detection (in-memory)
"""

import numpy as np
from sklearn.ensemble import IsolationForest
from typing import Dict, Tuple


class AnomalyDetector:
    """Isolation Forest-based anomaly detector for aircraft telemetry"""
    
    def __init__(self):
        """Initialize the anomaly detector"""
        self.model = None
        self.is_trained = False
        
    def _generate_synthetic_baseline_data(self, n_samples: int = 1000) -> np.ndarray:
        """
        Generate synthetic baseline telemetry data for training
        
        Args:
            n_samples: Number of training samples to generate
            
        Returns:
            Array of feature vectors [RPM, Pressure, Vibration, EGT]
        """
        np.random.seed(42)  # For reproducibility
        
        data = []
        for _ in range(n_samples):
            # Normal operating ranges
            sample = [
                np.random.uniform(8500, 9500),      # RPM
                np.random.uniform(1800, 2000),      # Pressure (PSI)
                np.random.uniform(0.1, 0.8),        # Vibration (mm/s)
                np.random.uniform(700, 800)         # EGT (Celsius)
            ]
            data.append(sample)
        
        return np.array(data)
    
    def train(self, n_samples: int = 1000, contamination: float = 0.1):
        """
        Train the Isolation Forest model on synthetic baseline data
        
        Args:
            n_samples: Number of training samples
            contamination: Expected proportion of anomalies (0.0 to 0.5)
        """
        # Generate synthetic baseline data
        training_data = self._generate_synthetic_baseline_data(n_samples)
        
        # Initialize and train Isolation Forest
        self.model = IsolationForest(
            n_estimators=100,
            contamination=contamination,
            random_state=42,
            max_features=4
        )
        
        self.model.fit(training_data)
        self.is_trained = True
        
    def detect_anomaly(self, telemetry: Dict[str, float]) -> Tuple[bool, float]:
        """
        Detect if telemetry contains an anomaly
        
        Args:
            telemetry: Dictionary with 'rpm', 'pressure', 'vibration', 'egt'
            
        Returns:
            Tuple of (is_anomaly: bool, anomaly_score: float)
            Score: -1 (anomaly) to 1 (normal), lower = more anomalous
        """
        if not self.is_trained:
            raise RuntimeError("Model must be trained before detection")
        
        # Extract features in same order as training
        features = np.array([[
            telemetry['rpm'],
            telemetry['pressure'],
            telemetry['vibration'],
            telemetry['egt']
        ]])
        
        # Predict anomaly (-1 for anomaly, 1 for normal)
        prediction = self.model.predict(features)[0]
        
        # Get anomaly score (decision function)
        score = self.model.score_samples(features)[0]
        
        # Normalize score to 0-1 range where 0 = normal, 1 = highly anomalous
        # Isolation Forest returns negative scores for anomalies
        anomaly_score = max(0.0, -score)  # Convert to positive scale
        
        is_anomaly = (prediction == -1)
        
        return is_anomaly, anomaly_score
    
    def get_feature_importance(self) -> Dict[str, float]:
        """
        Get feature importance (simplified - Isolation Forest doesn't provide direct importance)
        
        Returns:
            Dictionary with feature names and importance scores
        """
        if not self.is_trained:
            return {}
        
        # Isolation Forest doesn't provide direct feature importance
        # Return equal importance as placeholder
        return {
            'rpm': 0.25,
            'pressure': 0.25,
            'vibration': 0.25,
            'egt': 0.25
        }

