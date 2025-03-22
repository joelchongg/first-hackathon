from flask import Flask, render_template, jsonify, request
from app.monitor import SystemMonitor
from app.analyzer import SystemAnalyzer
from app.predictor import FailurePredictor
from app.optimizer import FaultToleranceOptimizer
import threading
import time
import os

app = Flask(__name__, 
    template_folder=os.path.abspath('templates'))  # Explicitly set template folder

monitor = SystemMonitor()
analyzer = SystemAnalyzer()
predictor = FailurePredictor()
optimizer = FaultToleranceOptimizer()

def background_monitoring():
    while True:
        try:
            metrics = monitor.get_detailed_metrics()
            if 'error' not in metrics:
                analyzer.analyze_metrics(metrics)
            time.sleep(2)
        except Exception as e:
            print(f"Monitoring error: {e}")

@app.route('/')
def dashboard():
    try:
        return render_template('dashboard.html')
    except Exception as e:
        print(f"Error rendering template: {e}")
        return f"Error loading dashboard: {str(e)}", 500

@app.route('/api/metrics')
def get_metrics():
    try:
        metrics = monitor.get_detailed_metrics()
        is_anomaly = analyzer.analyze_metrics(metrics) if 'error' not in metrics else True
        predictions = predictor.predict_failures(analyzer.metrics_history)
        recommendations = optimizer.generate_recommendations(predictions, metrics)
        
        return jsonify({
            'metrics': metrics,
            'health_score': analyzer.get_system_health_score(),
            'is_anomaly': is_anomaly,
            'predictions': predictions,
            'recommendations': recommendations
        })
    except Exception as e:
        print(f"Error in get_metrics: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/inject-fault/<fault_type>')
def inject_fault(fault_type):
    try:
        duration = request.args.get('duration', 30, type=int)
        success = monitor.inject_fault(fault_type, duration)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': f'Injected fault: {fault_type}, duration: {duration}s'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Unknown fault type: {fault_type}'
            }), 400
    except Exception as e:
        print(f"Error in inject_fault: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/active-faults')
def get_active_faults():
    try:
        return jsonify({
            'active_faults': monitor.get_active_faults()
        })
    except Exception as e:
        print(f"Error in get_active_faults: {e}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/recovery-status')
def get_recovery_status():
    try:
        return jsonify({
            'recovery_status': monitor.fault_injector.get_recovery_status()
        })
    except Exception as e:
        print(f"Error in get_recovery_status: {e}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/recovery-actions')
def get_recovery_actions():
    try:
        return jsonify({
            'recovery_actions': monitor.fault_injector.get_recovery_actions()
        })
    except Exception as e:
        print(f"Error in get_recovery_actions: {e}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    try:
        monitoring_thread = threading.Thread(target=background_monitoring, daemon=True)
        monitoring_thread.start()
        print("Starting server... Access the dashboard at http://localhost:5000")
        app.run(debug=True, host='0.0.0.0', port=5000)
    except Exception as e:
        print(f"Error starting server: {e}")
