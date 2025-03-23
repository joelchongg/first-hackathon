# app/predictor.py
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import logging
from collections import deque
import os
from datetime import datetime

class FailurePredictor:
    def __init__(self):
        # Initialize basic components
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.scaler = StandardScaler()
        
        # Data management
        self.metrics_history = deque(maxlen=60)  # Keep last 60 readings
        self.prediction_history = deque(maxlen=30)
        
        # Thresholds
        self.critical_threshold = 90.0
        self.warning_threshold = 70.0
        
        # Setup logging
        self._setup_logging()

    def _setup_logging(self):
        """Setup logging configuration"""
        try:
            if not os.path.exists('logs'):
                os.makedirs('logs')
            
            logging.basicConfig(
                filename='logs/predictor.log',
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
            self.logger = logging.getLogger('FailurePredictor')
        except Exception as e:
            print(f"Error setting up logging: {e}")

    def _prepare_features(self, metrics):
        """Prepare features for ML prediction"""
        try:
            features = [
                metrics['cpu_usage'],
                metrics['memory_usage'],
                metrics['disk_usage']
            ]
            return np.array(features).reshape(1, -1)
        except Exception as e:
            self.logger.error(f"Error preparing features: {e}")
            return None

    def _calculate_trends(self):
        """Calculate system metric trends"""
        if len(self.metrics_history) < 2:
            return {'cpu': 0.0, 'memory': 0.0, 'disk': 0.0}

        try:
            recent_metrics = list(self.metrics_history)[-5:]  # Last 5 readings
            
            trends = {
                'cpu': 0.0,
                'memory': 0.0,
                'disk': 0.0
            }
            
            for metric in ['cpu', 'memory', 'disk']:
                values = [m[f'{metric}_usage'] for m in recent_metrics]
                trend = (values[-1] - values[0]) / len(values)  # Simple linear trend
                trends[metric] = float(trend)
            
            return trends
            
        except Exception as e:
            self.logger.error(f"Error calculating trends: {e}")
            return {'cpu': 0.0, 'memory': 0.0, 'disk': 0.0}

    def _calculate_health_score(self, metrics):
        """Calculate overall system health score"""
        try:
            weights = {
                'cpu': 0.4,
                'memory': 0.3,
                'disk': 0.3
            }
            
            health_score = 100.0 - (
                weights['cpu'] * metrics['cpu_usage'] +
                weights['memory'] * metrics['memory_usage'] +
                weights['disk'] * metrics['disk_usage']
            )
            
            return max(0.0, min(100.0, health_score))
            
        except Exception as e:
            self.logger.error(f"Error calculating health score: {e}")
            return 100.0

    def predict_failures(self, metrics):
        """Generate failure predictions and system analysis"""
        try:
            # Store metrics in history
            self.metrics_history.append(metrics)
            
            # Prepare features
            features = self._prepare_features(metrics)
            if features is None:
                return self._generate_default_prediction()

            # Get anomaly score
            anomaly_score = self.model.fit_predict(features)[0]
            
            # Calculate failure probability
            base_probability = max(
                metrics['cpu_usage'],
                metrics['memory_usage'],
                metrics['disk_usage']
            ) / 100.0
            
            # Adjust probability based on anomaly detection
            failure_probability = min(1.0, base_probability * (1.0 if anomaly_score == -1 else 0.5))
            
            # Calculate trends
            trends = self._calculate_trends()
            
            # Calculate health score
            health_score = self._calculate_health_score(metrics)
            
            # Determine time to failure estimate
            time_to_failure = self._estimate_time_to_failure(
                failure_probability, 
                trends
            )
            
            # Calculate confidence score
            confidence_score = 1.0 - (failure_probability * 0.5)
            
            # Store prediction
            self.prediction_history.append({
                'timestamp': datetime.now(),
                'probability': failure_probability,
                'health_score': health_score
            })

            return {
                'failure_probability': float(failure_probability),
                'estimated_time_to_failure': time_to_failure,
                'confidence_score': float(confidence_score),
                'health_score': float(health_score),
                'trends': trends,
                'status': self._get_status(health_score)
            }

        except Exception as e:
            self.logger.error(f"Error in failure prediction: {e}")
            return self._generate_default_prediction()

    def _estimate_time_to_failure(self, probability, trends):
        """Estimate time until potential failure"""
        try:
            if probability > 0.9:
                return "Immediate risk"
            elif probability > 0.7:
                return "< 1 hour"
            elif probability > 0.5:
                return "1-3 hours"
            elif probability > 0.3:
                return "3-12 hours"
            else:
                return "No immediate risk"
                
        except Exception as e:
            self.logger.error(f"Error estimating time to failure: {e}")
            return "Unable to estimate"

    def _get_status(self, health_score):
        """Determine system status based on health score"""
        if health_score >= 80:
            return "healthy"
        elif health_score >= 60:
            return "warning"
        else:
            return "critical"

    def _generate_default_prediction(self):
        """Generate default prediction when analysis fails"""
        return {
            'failure_probability': 0.0,
            'estimated_time_to_failure': 'Unable to estimate',
            'confidence_score': 0.0,
            'health_score': 100.0,
            'trends': {'cpu': 0.0, 'memory': 0.0, 'disk': 0.0},
            'status': 'healthy'
        }

    def get_prediction_accuracy(self):
        """Get prediction accuracy metrics"""
        try:
            if not self.prediction_history:
                return {
                    'accuracy': 0.0,
                    'confidence': 0.0
                }

            recent_predictions = list(self.prediction_history)
            probabilities = [p['probability'] for p in recent_predictions]
            
            return {
                'accuracy': 1.0 - np.mean(probabilities),
                'confidence': np.mean([1.0 - p['probability'] for p in recent_predictions])
            }

        except Exception as e:
            self.logger.error(f"Error calculating prediction accuracy: {e}")
            return {
                'accuracy': 0.0,
                'confidence': 0.0
            }
