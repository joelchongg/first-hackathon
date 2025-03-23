# app/analyzer.py
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import logging
from collections import deque
import time
from datetime import datetime
import os

class SystemAnalyzer:
    def __init__(self):
        # Initialize ML components
        self.anomaly_detector = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        self.pattern_classifier = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
        self.scaler = StandardScaler()
        
        # Data management
        self.metrics_history = deque(maxlen=100)
        self.analysis_history = deque(maxlen=50)
        
        # Analysis windows
        self.short_window = 5    # Last 5 readings
        self.medium_window = 15  # Last 15 readings
        self.long_window = 30    # Last 30 readings
        
        # Thresholds
        self.critical_threshold = 90.0
        self.warning_threshold = 70.0
        
        # Setup logging
        self._setup_logging()

    def _setup_logging(self):
        """Initialize logging configuration"""
        try:
            if not os.path.exists('logs'):
                os.makedirs('logs')
                
            logging.basicConfig(
                filename='logs/analyzer.log',
                level=logging.INFO,
                format='%(asctime)s - %(levelname)s - %(message)s'
            )
            self.logger = logging.getLogger('SystemAnalyzer')
        except Exception as e:
            print(f"Error setting up logging: {e}")

    def analyze_metrics(self, metrics, predictions, optimizations):
        """Analyze system metrics and generate insights"""
        try:
            # Store metrics
            self.metrics_history.append(metrics)
            
            # Prepare analysis components
            features = self._prepare_features(metrics)
            if features is None:
                return self._generate_default_analysis()
            
            # Perform analysis
            anomaly_score = self._detect_anomalies(features)
            patterns = self._detect_patterns()
            trends = self._analyze_trends()
            insights = self._generate_insights(
                metrics, 
                predictions, 
                optimizations,
                anomaly_score
            )
            
            # Calculate health indicators
            health_indicators = self._calculate_health_indicators(
                metrics,
                anomaly_score,
                predictions
            )
            
            # Generate analysis result
            analysis = {
                'timestamp': datetime.now().isoformat(),
                'metrics': metrics,
                'health_indicators': health_indicators,
                'anomaly_score': float(anomaly_score),
                'patterns': patterns,
                'trends': trends,
                'insights': insights,
                'status': self._determine_status(health_indicators)
            }
            
            # Store analysis
            self.analysis_history.append(analysis)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in metric analysis: {e}")
            return self._generate_default_analysis()

    def _prepare_features(self, metrics):
        """Prepare features for analysis"""
        try:
            features = [
                metrics['cpu_usage'],
                metrics['memory_usage'],
                metrics['disk_usage']
            ]
            
            # Add derived features
            features.extend([
                metrics['cpu_usage'] / max(metrics['memory_usage'], 1),  # CPU/Memory ratio
                sum([metrics['cpu_usage'], 
                     metrics['memory_usage'], 
                     metrics['disk_usage']]) / 3,  # Average load
                np.std([metrics['cpu_usage'], 
                       metrics['memory_usage'], 
                       metrics['disk_usage']])  # Resource balance
            ])
            
            return np.array(features).reshape(1, -1)
            
        except Exception as e:
            self.logger.error(f"Error preparing features: {e}")
            return None

    def _detect_anomalies(self, features):
        """Detect system anomalies"""
        try:
            # Scale features
            scaled_features = self.scaler.fit_transform(features)
            
            # Detect anomalies
            score = self.anomaly_detector.fit_predict(scaled_features)[0]
            
            # Convert to normalized score (-1 to 1)
            return float(score)
            
        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {e}")
            return 0.0

    def _detect_patterns(self):
        """Detect system behavior patterns"""
        try:
            if len(self.metrics_history) < self.short_window:
                return {}
                
            patterns = {
                'cyclic_load': self._detect_cyclic_patterns(),
                'resource_correlation': self._analyze_resource_correlation(),
                'usage_patterns': self._analyze_usage_patterns()
            }
            
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error detecting patterns: {e}")
            return {}

    def _analyze_trends(self):
        """Analyze system metric trends"""
        try:
            if len(self.metrics_history) < 2:
                return self._generate_default_trends()
                
            trends = {}
            for window_name, window_size in [
                ('short_term', self.short_window),
                ('medium_term', self.medium_window),
                ('long_term', self.long_window)
            ]:
                if len(self.metrics_history) >= window_size:
                    window_data = list(self.metrics_history)[-window_size:]
                    trends[window_name] = {
                        'cpu': self._calculate_trend([m['cpu_usage'] for m in window_data]),
                        'memory': self._calculate_trend([m['memory_usage'] for m in window_data]),
                        'disk': self._calculate_trend([m['disk_usage'] for m in window_data])
                    }
                    
            return trends
            
        except Exception as e:
            self.logger.error(f"Error analyzing trends: {e}")
            return self._generate_default_trends()

    def _calculate_trend(self, values):
        """Calculate trend for a series of values"""
        try:
            if not values or len(values) < 2:
                return 0.0
                
            x = np.arange(len(values))
            y = np.array(values)
            
            # Calculate linear trend
            coefficients = np.polyfit(x, y, 1)
            slope = coefficients[0]
            
            return float(slope)
            
        except Exception as e:
            self.logger.error(f"Error calculating trend: {e}")
            return 0.0

    def _generate_insights(self, metrics, predictions, optimizations, anomaly_score):
        """Generate system insights"""
        try:
            insights = []
            
            # Resource usage insights
            if metrics['cpu_usage'] > self.critical_threshold:
                insights.append({
                    'type': 'critical',
                    'component': 'cpu',
                    'message': 'Critical CPU usage detected'
                })
            elif metrics['cpu_usage'] > self.warning_threshold:
                insights.append({
                    'type': 'warning',
                    'component': 'cpu',
                    'message': 'High CPU usage detected'
                })
                
            # Similar checks for memory and disk
            for resource in ['memory', 'disk']:
                usage = metrics[f'{resource}_usage']
                if usage > self.critical_threshold:
                    insights.append({
                        'type': 'critical',
                        'component': resource,
                        'message': f'Critical {resource} usage detected'
                    })
                elif usage > self.warning_threshold:
                    insights.append({
                        'type': 'warning',
                        'component': resource,
                        'message': f'High {resource} usage detected'
                    })
            
            # Anomaly insights
            if anomaly_score == -1:
                insights.append({
                    'type': 'warning',
                    'component': 'system',
                    'message': 'System behavior anomaly detected'
                })
            
            # Prediction insights
            if predictions and predictions.get('failure_probability', 0) > 0.7:
                insights.append({
                    'type': 'critical',
                    'component': 'prediction',
                    'message': 'High failure probability predicted'
                })
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating insights: {e}")
            return []

    def _calculate_health_indicators(self, metrics, anomaly_score, predictions):
        """Calculate system health indicators"""
        try:
            # Base health score
            base_health = 100.0 - (
                0.4 * metrics['cpu_usage'] +
                0.3 * metrics['memory_usage'] +
                0.3 * metrics['disk_usage']
            )
            
            # Adjust for anomalies
            anomaly_factor = 1.0 if anomaly_score == 1 else 0.8
            
            # Adjust for predictions
            prediction_factor = 1.0
            if predictions and 'failure_probability' in predictions:
                prediction_factor = 1.0 - (predictions['failure_probability'] * 0.5)
            
            # Calculate final health score
            health_score = base_health * anomaly_factor * prediction_factor
            
            return {
                'overall_health': max(0.0, min(100.0, health_score)),
                'resource_health': {
                    'cpu': 100.0 - metrics['cpu_usage'],
                    'memory': 100.0 - metrics['memory_usage'],
                    'disk': 100.0 - metrics['disk_usage']
                },
                'anomaly_factor': anomaly_factor,
                'prediction_factor': prediction_factor
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating health indicators: {e}")
            return self._generate_default_health_indicators()

    def _determine_status(self, health_indicators):
        """Determine overall system status"""
        try:
            health_score = health_indicators['overall_health']
            
            if health_score >= 80:
                return 'healthy'
            elif health_score >= 60:
                return 'warning'
            else:
                return 'critical'
                
        except Exception as e:
            self.logger.error(f"Error determining status: {e}")
            return 'unknown'

    def _detect_cyclic_patterns(self):
        """Detect cyclic load patterns"""
        try:
            if len(self.metrics_history) < self.medium_window:
                return {}
                
            recent_data = list(self.metrics_history)[-self.medium_window:]
            
            patterns = {}
            for metric in ['cpu_usage', 'memory_usage', 'disk_usage']:
                values = [m[metric] for m in recent_data]
                patterns[metric] = {
                    'periodic': self._check_periodicity(values),
                    'variance': float(np.var(values))
                }
                
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error detecting cyclic patterns: {e}")
            return {}

    def _analyze_resource_correlation(self):
        """Analyze correlation between resources"""
        try:
            if len(self.metrics_history) < self.short_window:
                return {}
                
            recent_data = list(self.metrics_history)[-self.short_window:]
            
            cpu_values = [m['cpu_usage'] for m in recent_data]
            memory_values = [m['memory_usage'] for m in recent_data]
            disk_values = [m['disk_usage'] for m in recent_data]
            
            correlations = {
                'cpu_memory': float(np.corrcoef(cpu_values, memory_values)[0, 1]),
                'cpu_disk': float(np.corrcoef(cpu_values, disk_values)[0, 1]),
                'memory_disk': float(np.corrcoef(memory_values, disk_values)[0, 1])
            }
            
            return correlations
            
        except Exception as e:
            self.logger.error(f"Error analyzing resource correlation: {e}")
            return {}

    def _analyze_usage_patterns(self):
        """Analyze resource usage patterns"""
        try:
            if len(self.metrics_history) < self.medium_window:
                return {}
                
            patterns = {}
            for metric in ['cpu_usage', 'memory_usage', 'disk_usage']:
                values = [m[metric] for m in self.metrics_history]
                patterns[metric] = {
                    'mean': float(np.mean(values)),
                    'std': float(np.std(values)),
                    'min': float(np.min(values)),
                    'max': float(np.max(values))
                }
                
            return patterns
            
        except Exception as e:
            self.logger.error(f"Error analyzing usage patterns: {e}")
            return {}

    def _check_periodicity(self, values):
        """Check for periodic behavior in values"""
        try:
            if len(values) < 4:
                return False
                
            # Simple periodicity check
            diffs = np.diff(values)
            sign_changes = np.diff(np.signbit(diffs))
            
            return bool(np.sum(sign_changes) > len(values) * 0.4)
            
        except Exception as e:
            self.logger.error(f"Error checking periodicity: {e}")
            return False

    def _generate_default_analysis(self):
        """Generate default analysis result"""
        return {
            'timestamp': datetime.now().isoformat(),
            'metrics': {},
            'health_indicators': self._generate_default_health_indicators(),
            'anomaly_score': 0.0,
            'patterns': {},
            'trends': self._generate_default_trends(),
            'insights': [],
            'status': 'unknown'
        }

    def _generate_default_health_indicators(self):
        """Generate default health indicators"""
        return {
            'overall_health': 100.0,
            'resource_health': {
                'cpu': 100.0,
                'memory': 100.0,
                'disk': 100.0
            },
            'anomaly_factor': 1.0,
            'prediction_factor': 1.0
        }

    def _generate_default_trends(self):
        """Generate default trends"""
        return {
            'short_term': {'cpu': 0.0, 'memory': 0.0, 'disk': 0.0},
            'medium_term': {'cpu': 0.0, 'memory': 0.0, 'disk': 0.0},
            'long_term': {'cpu': 0.0, 'memory': 0.0, 'disk': 0.0}
        }

    def get_analysis_summary(self):
        """Get summary of recent analysis"""
        try:
            if not self.analysis_history:
                return self._generate_default_analysis()
                
            latest = self.analysis_history[-1]
            return {
                'current_status': latest['status'],
                'health_score': latest['health_indicators']['overall_health'],
                'anomalies_detected': latest['anomaly_score'] == -1,
                'critical_insights': [
                    i for i in latest['insights'] 
                    if i['type'] == 'critical'
                ],
                'trends': latest['trends']
            }
            
        except Exception as e:
            self.logger.error(f"Error getting analysis summary: {e}")
            return self._generate_default_analysis()
