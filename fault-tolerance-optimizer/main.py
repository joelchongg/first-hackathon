from flask import Flask, render_template, jsonify
from flask_cors import CORS
import threading
import time
import psutil
import logging
from sklearn.ensemble import IsolationForest
import numpy as np
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configure basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variables for storing metrics
metrics_history = []
anomaly_detector = IsolationForest(contamination=0.1, random_state=42)
active_remediation = False

def get_system_metrics():
    """Collect basic system metrics"""
    try:
        return {
            'cpu_usage': psutil.cpu_percent(),
            'memory_usage': psutil.virtual_memory().percent,
            'disk_usage': psutil.disk_usage('/').percent,
            'timestamp': time.time()
        }
    except Exception as e:
        logger.error(f"Error collecting metrics: {e}")
        return None

def predict_failures(metrics_history):
    """Basic ML-based failure prediction"""
    if len(metrics_history) < 2:
        return {'failure_probability': 0.0}
        
    try:
        # Extract features for ML
        features = [[m['cpu_usage'], m['memory_usage'], m['disk_usage']] 
                   for m in metrics_history]
        
        # Fit and predict
        anomaly_detector.fit(features)
        scores = anomaly_detector.score_samples(features)
        
        # Convert scores to probability (higher score = more likely to fail)
        latest_score = scores[-1]
        probability = 1 - (latest_score - min(scores)) / (max(scores) - min(scores))
        
        return {'failure_probability': float(probability)}
        
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        return {'failure_probability': 0.0}

def auto_remediate(metrics):
    """Simple AI remediation based on thresholds"""
    global active_remediation
    
    if active_remediation:
        return
        
    try:
        if metrics['cpu_usage'] > 90 or metrics['memory_usage'] > 90:
            active_remediation = True
            logger.info("Starting automatic remediation...")
            
            # Simulate remediation action
            time.sleep(2)
            
            active_remediation = False
            logger.info("Remediation completed")
            
    except Exception as e:
        logger.error(f"Remediation error: {e}")
        active_remediation = False

def background_monitoring():
    """Background thread for system monitoring"""
    while True:
        try:
            # Collect current metrics
            metrics = get_system_metrics()
            if metrics:
                metrics_history.append(metrics)
                
                # Keep last 60 readings
                if len(metrics_history) > 60:
                    metrics_history.pop(0)
                
                # Get ML predictions
                prediction = predict_failures(metrics_history)
                
                # Log status
                logger.info(
                    f"System Status - "
                    f"CPU: {metrics['cpu_usage']}% | "
                    f"MEM: {metrics['memory_usage']}% | "
                    f"Failure Prob: {prediction['failure_probability']:.2f}"
                )
                
                # Auto-remediate if necessary
                if prediction['failure_probability'] > 0.8:
                    auto_remediate(metrics)
                    
            time.sleep(2)
            
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            time.sleep(5)

@app.route('/')
def home():
    return render_template('dashboard.html')

@app.route('/api/metrics')
def get_metrics():
    """API endpoint for current metrics and predictions"""
    try:
        current_metrics = get_system_metrics()
        if not current_metrics:
            return jsonify({'error': 'Failed to collect metrics'}), 500
            
        prediction = predict_failures(metrics_history)
        
        return jsonify({
            'metrics': current_metrics,
            'prediction': prediction,
            'remediation_active': active_remediation
        })
        
    except Exception as e:
        logger.error(f"API error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health')
def health_check():
    """Basic health check endpoint"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    try:
        # Start background monitoring thread
        monitoring_thread = threading.Thread(
            target=background_monitoring, 
            daemon=True
        )
        monitoring_thread.start()
        
        # Start Flask server
        logger.info("Starting server... Access dashboard at http://localhost:5000")
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except Exception as e:
        logger.error(f"Server error: {e}")
