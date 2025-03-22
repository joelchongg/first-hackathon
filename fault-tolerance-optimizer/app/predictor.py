class FailurePredictor:
    def predict_failures(self, metrics_history):
        if not metrics_history:
            return {
                'failure_probability': 0.0,
                'estimated_time_to_failure': 'No immediate risk'
            }
        
        latest = metrics_history[-1]
        if 'error' in latest:
            return {
                'failure_probability': 1.0,
                'estimated_time_to_failure': 'System error detected'
            }
        
        # Calculate highest usage from numeric metrics
        numeric_values = [
            float(value) 
            for value in latest.values() 
            if isinstance(value, (int, float))
        ]
        
        if not numeric_values:
            return {
                'failure_probability': 0.0,
                'estimated_time_to_failure': 'No metrics available'
            }
            
        highest_usage = max(numeric_values)
        
        if highest_usage > 90.0:
            return {
                'failure_probability': 0.8,
                'estimated_time_to_failure': '1 hour'
            }
        elif highest_usage > 80.0:
            return {
                'failure_probability': 0.5,
                'estimated_time_to_failure': '3 hours'
            }
        else:
            return {
                'failure_probability': 0.1,
                'estimated_time_to_failure': 'No immediate risk'
            }
